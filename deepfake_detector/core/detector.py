import cv2
import io
import numpy as np
from PIL import Image

# Verdicts
REAL = "REAL"
FAKE = "FAKE"
UNCERTAIN = "UNCERTAIN"

THRESHOLD_FAKE = 0.55      # score >= 0.55 → FAKE
THRESHOLD_UNCERTAIN = 0.28  # score >= 0.28 → UNCERTAIN, else REAL


class DeepfakeDetector:
    """
    Heuristic deepfake detector.
    Principle: real images should score very low (0.02–0.15) on every
    dimension.  Only genuinely anomalous signals raise a score above 0.40.
    """

    WEIGHTS = {
        "frequency":    0.12,
        "compression":  0.22,
        "noise":        0.22,
        "ela":          0.22,   # Error Level Analysis — strongest for edited/AI images
        "texture":      0.12,   # Multi-scale texture consistency
        "color":        0.06,
        "edge":         0.04,
    }

    # ── Frequency Domain ──────────────────────────────────────────────────────

    def analyze_frequency_domain(self, img: np.ndarray) -> dict:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(np.float32)
        f = np.fft.fft2(gray)
        fshift = np.fft.fftshift(f)
        power = np.abs(fshift) ** 2
        magnitude_log = np.log1p(np.abs(fshift))

        rows, cols = gray.shape
        crow, ccol = rows // 2, cols // 2
        y_idx, x_idx = np.indices((rows, cols))
        r = np.sqrt((x_idx - ccol) ** 2 + (y_idx - crow) ** 2).astype(int)
        max_r = min(crow, ccol) - 1
        mask = r <= max_r
        tbin = np.bincount(r[mask].ravel(), power[mask].ravel())
        nr = np.bincount(r[mask].ravel())
        radial_prof = (tbin / (nr + 1e-9))[1:]

        # GAN grid artifacts → periodic spikes in radial power profile
        spike_score = 0.0
        if len(radial_prof) > 20:
            smooth = np.convolve(radial_prof, np.ones(9) / 9, mode="same")
            residual = np.abs(radial_prof - smooth) / (smooth + 1e-9)
            max_spike = float(residual.max())
            # Only flag spikes > 4× the smoothed baseline
            if max_spike > 4.0:
                spike_score = float(np.clip((max_spike - 4.0) / 6.0, 0, 1))

        # High-frequency energy ratio: real photos ~0.70–0.95
        r_low = max_r // 8
        low_e = float(power[r <= r_low].sum())
        high_e = float(power[(r > r_low) & (r <= max_r)].sum())
        high_freq_ratio = high_e / (low_e + high_e + 1e-9)
        # Only flag extreme deficit of high-freq energy
        hfr_score = float(np.clip((0.60 - high_freq_ratio) / 0.30, 0, 1)) if high_freq_ratio < 0.60 else 0.0

        score = float(np.clip(0.75 * spike_score + 0.25 * hfr_score, 0, 1))

        return {
            "score": round(score, 4),
            "fft_magnitude": magnitude_log,
            "high_freq_ratio": round(high_freq_ratio, 4),
            "spike_score": round(spike_score, 4),
        }

    # ── Compression Artifacts ─────────────────────────────────────────────────

    def analyze_compression_artifacts(self, img: np.ndarray) -> dict:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(np.float32)
        block_size = 8
        h, w = gray.shape
        h_t = (h // block_size) * block_size
        w_t = (w // block_size) * block_size
        gray_t = gray[:h_t, :w_t]

        h_bnd = np.abs(np.diff(gray_t[block_size - 1::block_size, :], axis=0)).mean()
        h_int = np.abs(np.diff(gray_t, axis=0)).mean() + 1e-9
        v_bnd = np.abs(np.diff(gray_t[:, block_size - 1::block_size], axis=1)).mean()
        v_int = np.abs(np.diff(gray_t, axis=1)).mean() + 1e-9
        block_ratio = float(((h_bnd / h_int) + (v_bnd / v_int)) / 2)

        # GAN images are "too clean" → block_ratio << 0.15
        # Real JPEG camera photos: 0.60–1.80 → score ≈ 0.02
        if block_ratio < 0.10:
            score = float(np.clip((0.10 - block_ratio) / 0.10, 0, 1)) * 0.90
        elif block_ratio < 0.25:
            score = float(np.clip((0.25 - block_ratio) / 0.15, 0, 1)) * 0.50
        elif block_ratio > 3.5:
            score = float(np.clip((block_ratio - 3.5) / 4.0, 0, 1)) * 0.40
        else:
            score = 0.02

        return {
            "score": round(float(np.clip(score, 0, 1)), 4),
            "block_artifact_score": round(block_ratio, 4),
        }

    # ── Noise Pattern ─────────────────────────────────────────────────────────

    def analyze_noise_pattern(self, img: np.ndarray) -> dict:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(np.float32)
        laplacian = cv2.Laplacian(gray, cv2.CV_32F)
        noise_std = float(np.std(laplacian))

        # Real camera photos: noise_std 5–50+
        # GAN synthetic images: often < 0.8 (almost no sensor noise)
        if noise_std < 0.5:
            score = 0.92
        elif noise_std < 1.0:
            score = 0.65
        elif noise_std < 2.0:
            score = 0.30
        else:
            score = 0.03   # normal — no penalty

        return {
            "score": round(float(np.clip(score, 0, 1)), 4),
            "noise_std": round(noise_std, 4),
            "noise_uniformity": 0.0,
        }

    # ── Color Distribution ────────────────────────────────────────────────────

    def analyze_color_distribution(self, img: np.ndarray) -> dict:
        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV).astype(np.float32)
        sat_std = float(np.std(hsv[:, :, 1]))
        val_std = float(np.std(hsv[:, :, 2]))

        r = img[:, :, 0].astype(float).ravel()
        g = img[:, :, 1].astype(float).ravel()
        b = img[:, :, 2].astype(float).ravel()

        def corr(a, x):
            if np.std(a) < 1e-9 or np.std(x) < 1e-9:
                return 0.0
            return float(np.corrcoef(a, x)[0, 1])

        mean_corr = (abs(corr(r, g)) + abs(corr(g, b)) + abs(corr(r, b))) / 3

        # Only flag nearly perfectly correlated channels (synthetic gradient/grayscale)
        if mean_corr > 0.97:
            score = float(np.clip((mean_corr - 0.97) / 0.03, 0, 1)) * 0.65
        elif mean_corr < 0.25:
            score = float(np.clip((0.25 - mean_corr) / 0.25, 0, 1)) * 0.35
        else:
            score = 0.03

        return {
            "score": round(float(np.clip(score, 0, 1)), 4),
            "saturation_std": round(sat_std, 4),
            "value_std": round(val_std, 4),
            "channel_correlation": round(mean_corr, 4),
        }

    # ── Edge Consistency ──────────────────────────────────────────────────────

    def analyze_edge_consistency(self, img: np.ndarray) -> dict:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = float(edges.mean()) / 255.0

        # Real camera photos: 0.01–0.45 (wide natural range)
        # Completely edge-less synthetic images: < 0.003
        if edge_density < 0.003:
            density_score = 0.80
        elif edge_density < 0.008:
            density_score = 0.35
        else:
            density_score = 0.03

        sx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        sy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        angles = np.arctan2(sy, sx)
        hist, _ = np.histogram(angles, bins=8, range=(-np.pi, np.pi))
        hist_norm = hist.astype(float) / (hist.sum() + 1e-9)
        orient_score = float(np.clip(np.std(hist_norm) / (1.0 / 8), 0, 1)) * 0.25

        score = float(np.clip(0.65 * density_score + 0.35 * orient_score, 0, 1))

        return {
            "score": round(score, 4),
            "edge_density": round(edge_density, 4),
            "orientation_uniformity": round(orient_score, 4),
            "edges": edges,
        }

    # ── ELA (Error Level Analysis) ────────────────────────────────────────────

    def analyze_ela(self, img: np.ndarray) -> dict:
        """
        Save image at two JPEG qualities and compare the error maps.
        AI-generated images have unnaturally uniform ELA because they were
        never JPEG-encoded by a camera; manipulated regions show elevated
        or inconsistent error levels compared to the rest of the image.
        """
        pil_img = Image.fromarray(img)

        def _to_jpeg(quality: int) -> np.ndarray:
            buf = io.BytesIO()
            pil_img.save(buf, "JPEG", quality=quality)
            buf.seek(0)
            return np.array(Image.open(buf).convert("RGB"))

        img_hi = _to_jpeg(95)
        img_lo = _to_jpeg(75)
        ela_map = np.abs(img_hi.astype(float) - img_lo.astype(float))
        ela_gray = ela_map.mean(axis=2)

        ela_mean = float(ela_gray.mean())
        ela_std = float(ela_gray.std())

        # Divide into 4×4 patch grid; check coefficient of variation of patch means
        h, w = ela_gray.shape
        patch_means = []
        for i in range(4):
            for j in range(4):
                p = ela_gray[i * h // 4:(i + 1) * h // 4, j * w // 4:(j + 1) * w // 4]
                patch_means.append(float(p.mean()))

        patch_cv = float(np.std(patch_means) / (np.mean(patch_means) + 1e-9))

        # Real camera JPEG: high patch_cv (natural scenes create unequal error levels)
        # GAN / synthetic image: unnaturally uniform ELA (low patch_cv) → suspicious
        if patch_cv < 0.30:
            score = float(np.clip((0.30 - patch_cv) / 0.30, 0, 1)) * 0.85
        elif patch_cv < 0.55:
            score = 0.25
        else:
            score = 0.04   # natural heterogeneous ELA

        return {
            "score": round(float(np.clip(score, 0, 1)), 4),
            "ela_mean": round(ela_mean, 4),
            "ela_std": round(ela_std, 4),
            "ela_patch_cv": round(patch_cv, 4),
            "ela_map": (ela_gray * 5).clip(0, 255).astype(np.uint8),  # brightened for display
        }

    # ── Multi-scale Texture ───────────────────────────────────────────────────

    def analyze_texture(self, img: np.ndarray) -> dict:
        """
        Real photos exhibit rich texture at every spatial scale.
        GAN images are often unnaturally smooth at fine scales while
        appearing detailed at coarse scales — a different ratio than real.
        """
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(np.float32)

        variances = []
        for ksize in [3, 7, 15, 31]:
            blurred = cv2.GaussianBlur(gray, (ksize, ksize), 0)
            local_var = (gray - blurred) ** 2
            variances.append(float(local_var.mean()))

        # Fine-to-coarse variance ratio
        fine_var = variances[0]
        coarse_var = variances[-1]
        ratio = fine_var / (coarse_var + 1e-9)

        # Real photos: ratio typically 0.3–4.0
        # GAN images: ratio < 0.1 (fine scale is too smooth) or > 8 (over-sharpened)
        if ratio < 0.10:
            score = float(np.clip((0.10 - ratio) / 0.10, 0, 1)) * 0.80
        elif ratio > 8.0:
            score = float(np.clip((ratio - 8.0) / 8.0, 0, 1)) * 0.55
        else:
            score = 0.04

        return {
            "score": round(float(np.clip(score, 0, 1)), 4),
            "fine_var": round(fine_var, 4),
            "coarse_var": round(coarse_var, 4),
            "texture_ratio": round(ratio, 4),
        }

    # ── Temporal Consistency ──────────────────────────────────────────────────

    def analyze_face_consistency(self, frames: list) -> dict:
        if len(frames) < 2:
            return {"score": 0.0, "mean_similarity": 1.0, "inconsistency_detected": False}

        similarities = []
        for i in range(len(frames) - 1):
            a = cv2.resize(cv2.cvtColor(frames[i], cv2.COLOR_RGB2GRAY), (64, 64)).astype(np.float32)
            b = cv2.resize(cv2.cvtColor(frames[i + 1], cv2.COLOR_RGB2GRAY), (64, 64)).astype(np.float32)
            denom = (np.std(a) * np.std(b) + 1e-9) * a.size
            sim = float(np.clip(np.sum((a - a.mean()) * (b - b.mean())) / denom, 0, 1))
            similarities.append(sim)

        mean_sim = float(np.mean(similarities))
        score = float(np.clip(1.0 - mean_sim, 0, 1))

        return {
            "score": round(score, 4),
            "mean_similarity": round(mean_sim, 4),
            "inconsistency_detected": mean_sim < 0.5 or float(np.var(similarities)) > 0.05,
        }

    # ── Summary / Explanation ─────────────────────────────────────────────────

    def generate_summary(self, result: dict) -> dict:
        breakdown = result.get("analysis_breakdown", {})
        verdict = result.get("final_verdict", REAL)
        confidence = result.get("confidence", 0.0)

        def _status(s):
            if s > 0.55:
                return "SUSPICIOUS", "🔴"
            elif s > 0.25:
                return "MODERATE", "🟡"
            return "NORMAL", "🟢"

        TEXTS = {
            "Frequency Domain": {
                "SUSPICIOUS": "Periodic spectral peaks detected in the FFT power spectrum — a fingerprint of transposed-convolution grid artifacts produced by GAN architectures. Natural photographs never exhibit these regular interference patterns.",
                "MODERATE": "Minor spectral irregularities detected. The frequency distribution shows a slight deviation from expected natural patterns, possibly from post-processing or light manipulation.",
                "NORMAL": "Frequency spectrum shows no anomalous peaks. Power distribution follows natural photographic characteristics.",
            },
            "Compression Artifacts": {
                "SUSPICIOUS": "8×8 DCT block boundaries are abnormally clean (block ratio << 0.15). GAN-generated images skip the lossy compression pipeline entirely, producing images that look 'too pristine' at block boundaries — unlike any real camera-captured JPEG.",
                "MODERATE": "Compression artifact levels are slightly below the expected range for camera-captured photos. Could indicate light manipulation or unusual compression settings.",
                "NORMAL": "Compression artifact ratio is consistent with normal JPEG camera output. No anomalous block boundaries detected.",
            },
            "Noise Pattern": {
                "SUSPICIOUS": "Laplacian noise standard deviation is extremely low (< 1.0). Real camera sensors always inject measurable photon shot noise and sensor noise (PRNU). This level of smoothness is only achievable synthetically.",
                "MODERATE": "Noise levels are lower than expected for a real camera. Could indicate heavy post-processing, denoising filters, or AI generation.",
                "NORMAL": "Noise standard deviation is within the expected range for camera-captured imagery. Natural sensor noise is present.",
            },
            "Color Distribution": {
                "SUSPICIOUS": "RGB inter-channel correlation is near-perfect (> 0.97), indicating artificially flat or synthetic colour mapping. Real photographic scenes produce diverse, non-linearly correlated colour channels.",
                "MODERATE": "Slight colour channel irregularities. Inter-channel correlation or saturation distribution deviates mildly from natural photographic norms.",
                "NORMAL": "Colour distribution across RGB and HSV channels is natural, with appropriate inter-channel correlation for real-world scenes.",
            },
            "Edge Consistency": {
                "SUSPICIOUS": "Edge density is near zero (< 0.003). Completely edge-free images do not occur naturally in photographs — even featureless backgrounds have micro-texture edges. This is characteristic of synthetic flat regions.",
                "MODERATE": "Edge density is unusually low. The image may have been generated with very smooth regions or undergo aggressive blurring.",
                "NORMAL": "Edge density and gradient orientation distribution are consistent with natural photographic content.",
            },
            "ELA (Error Analysis)": {
                "SUSPICIOUS": "Error Level Analysis (ELA) reveals unnaturally uniform JPEG re-encoding differences across all image regions. Real camera photos always have heterogeneous ELA because different scene content compresses at different rates. GAN-generated and AI-edited images lack this natural variation, producing a flat, uniform ELA map.",
                "MODERATE": "ELA shows mildly uniform error distribution across image patches. This could indicate light post-processing or AI upscaling, but is not conclusive alone.",
                "NORMAL": "ELA patch coefficient of variation is healthy — different regions compress at different rates, consistent with a genuine, unmanipulated photograph.",
            },
            "Texture Consistency": {
                "SUSPICIOUS": "Multi-scale texture analysis shows an abnormal fine-to-coarse variance ratio. GAN architectures often produce images that appear detailed at medium scale but lack micro-texture at fine scale — or are unnaturally over-sharpened. Real photographs have smooth variance transitions across spatial scales.",
                "MODERATE": "Texture variance ratio across spatial scales is slightly outside the natural range. Could indicate AI upscaling, sharpening, or partial generation.",
                "NORMAL": "Multi-scale texture variance transitions naturally from fine to coarse scale, consistent with authentic photographic capture.",
            },
            "Temporal Consistency": {
                "SUSPICIOUS": "Significant frame-to-frame inconsistencies detected. Face-swap deepfake generators introduce subtle flickering at synthetic boundaries that manifests as low inter-frame correlation.",
                "MODERATE": "Some temporal inconsistency between frames. Could indicate video processing or light deepfake artifacts.",
                "NORMAL": "Frame-to-frame consistency is high, consistent with natural continuous video capture.",
            },
        }

        dim_explanations = {}
        for dim, score in breakdown.items():
            status, icon = _status(score)
            texts = TEXTS.get(dim, {})
            dim_explanations[dim] = {
                "status": status,
                "icon": icon,
                "score": score,
                "explanation": texts.get(status, "No additional detail available."),
            }

        sorted_dims = sorted(dim_explanations.items(), key=lambda x: x[1]["score"], reverse=True)
        key_factors = [(d, info["score"]) for d, info in sorted_dims[:3]]
        suspicious = [d for d, info in sorted_dims if info["score"] > 0.50]

        if verdict == FAKE:
            if suspicious:
                verdict_reason = (
                    f"Classified as FAKE — strong anomalies in: {', '.join(suspicious[:3])}. "
                    f"These patterns do not occur in authentic camera captures and are characteristic "
                    f"of AI-generated imagery (score: {confidence:.1f}%)."
                )
            else:
                verdict_reason = (
                    f"Classified as FAKE based on cumulative weak signals across multiple dimensions "
                    f"(score: {confidence:.1f}%). No single dimension was conclusive."
                )
        elif verdict == UNCERTAIN:
            verdict_reason = (
                f"Result is UNCERTAIN (score: {confidence:.1f}%). "
                f"Some dimensions show minor anomalies but none are conclusive. "
                f"This could be a real image with unusual properties, or a high-quality deepfake. "
                f"Manual expert review is recommended."
            )
        else:
            verdict_reason = (
                f"Classified as REAL — all analysis dimensions are within natural photographic ranges "
                f"(score: {confidence:.1f}%). No significant deepfake artifacts detected."
            )

        if confidence > 80:
            confidence_note = "High confidence — multiple dimensions agree strongly."
        elif confidence > 50:
            confidence_note = "Moderate confidence — primary indicators are consistent."
        elif confidence > 28:
            confidence_note = "Low confidence (UNCERTAIN zone) — manual expert review strongly recommended."
        else:
            confidence_note = "High confidence this is authentic — all metrics within normal range."

        return {
            "verdict": verdict,
            "verdict_reason": verdict_reason,
            "dimension_explanations": dim_explanations,
            "key_factors": key_factors,
            "confidence_note": confidence_note,
        }

    # ── Combined Scoring ──────────────────────────────────────────────────────

    def _final_verdict(self, score: float) -> str:
        if score >= THRESHOLD_FAKE:
            return FAKE
        elif score >= THRESHOLD_UNCERTAIN:
            return UNCERTAIN
        return REAL

    def analyze_frame(self, frame: np.ndarray) -> dict:
        freq = self.analyze_frequency_domain(frame)
        comp = self.analyze_compression_artifacts(frame)
        noise = self.analyze_noise_pattern(frame)
        ela = self.analyze_ela(frame)
        texture = self.analyze_texture(frame)
        color = self.analyze_color_distribution(frame)
        edge = self.analyze_edge_consistency(frame)

        w = self.WEIGHTS
        overall = (
            freq["score"]    * w["frequency"]
            + comp["score"]  * w["compression"]
            + noise["score"] * w["noise"]
            + ela["score"]   * w["ela"]
            + texture["score"] * w["texture"]
            + color["score"] * w["color"]
            + edge["score"]  * w["edge"]
        )
        overall = float(np.clip(overall, 0, 1))
        verdict = self._final_verdict(overall)

        return {
            "frequency": freq,
            "compression": comp,
            "noise": noise,
            "ela": ela,
            "texture": texture,
            "color": color,
            "edge": edge,
            "overall_score": round(overall, 4),
            "is_fake": verdict == FAKE,
            "final_verdict": verdict,
            "confidence": round(overall * 100, 1),
        }

    def _build_breakdown(self, result: dict) -> dict:
        return {
            "Frequency Domain":      result["frequency"]["score"],
            "Compression Artifacts": result["compression"]["score"],
            "Noise Pattern":         result["noise"]["score"],
            "ELA (Error Analysis)":  result["ela"]["score"],
            "Texture Consistency":   result["texture"]["score"],
            "Color Distribution":    result["color"]["score"],
            "Edge Consistency":      result["edge"]["score"],
        }

    def analyze_image(self, img_input) -> dict:
        if isinstance(img_input, np.ndarray):
            img = img_input
        elif isinstance(img_input, str):
            bgr = cv2.imread(img_input)
            img = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        elif hasattr(img_input, "read"):
            arr = np.frombuffer(img_input.read(), np.uint8)
            bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            img = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        else:
            img = np.array(img_input)

        result = self.analyze_frame(img)
        result["image"] = img
        result["analysis_breakdown"] = self._build_breakdown(result)
        result["summary"] = self.generate_summary(result)
        return result

    def analyze_video_frames(self, frames: list) -> dict:
        if not frames:
            return {}

        frame_results = [self.analyze_frame(f) for f in frames]
        scores = [r["overall_score"] for r in frame_results]
        mean_score = float(np.mean(scores))

        temporal = self.analyze_face_consistency(frames)
        # Temporal adds 10% weight on top of the frame scores
        final_score = float(np.clip(0.90 * mean_score + 0.10 * temporal["score"], 0, 1))
        verdict = self._final_verdict(final_score)

        result = {
            "frame_results": frame_results,
            "frame_scores": scores,
            "mean_score": round(mean_score, 4),
            "temporal_score": round(temporal["score"], 4),
            "temporal_analysis": temporal,
            "final_score": round(final_score, 4),
            "final_verdict": verdict,
            "confidence": round(final_score * 100, 1),
            "is_fake": verdict == FAKE,
            "analysis_breakdown": {
                "Frequency Domain":      float(np.mean([r["frequency"]["score"] for r in frame_results])),
                "Compression Artifacts": float(np.mean([r["compression"]["score"] for r in frame_results])),
                "Noise Pattern":         float(np.mean([r["noise"]["score"] for r in frame_results])),
                "ELA (Error Analysis)":  float(np.mean([r["ela"]["score"] for r in frame_results])),
                "Texture Consistency":   float(np.mean([r["texture"]["score"] for r in frame_results])),
                "Color Distribution":    float(np.mean([r["color"]["score"] for r in frame_results])),
                "Edge Consistency":      float(np.mean([r["edge"]["score"] for r in frame_results])),
                "Temporal Consistency":  temporal["score"],
            },
        }
        result["summary"] = self.generate_summary(result)
        return result

    # ── Synthetic Demo ────────────────────────────────────────────────────────

    @staticmethod
    def generate_synthetic_fake() -> np.ndarray:
        """Synthetic image with strong GAN-like artifacts for demo purposes."""
        rng = np.random.default_rng(42)
        # Near-zero noise (noise_std will be < 0.5 → score 0.92)
        img = np.full((256, 256, 3), 140, dtype=np.uint8)
        tiny_noise = rng.normal(0, 0.3, img.shape).astype(np.int16)
        img = np.clip(img.astype(np.int16) + tiny_noise, 0, 255).astype(np.uint8)
        # Strong 8×8 block pattern → very low block_ratio (score 0.85+)
        # + clear spectral peaks in FFT (score 0.50+)
        for i in range(0, 256, 8):
            for j in range(0, 256, 8):
                val = int(25 * np.sin(2 * np.pi * i / 64) * np.cos(2 * np.pi * j / 64))
                img[i:i + 8, j:j + 8] = np.clip(
                    img[i:i + 8, j:j + 8].astype(np.int16) + val, 0, 255
                ).astype(np.uint8)
        return img
