import time
import os
import cv2
import numpy as np
import scipy.fft
import scipy.stats
from tqdm import tqdm
from photo_quality_analyzer_core.analyzer import SUPPORTED_EXTENSIONS
import rawpy

FOLDER = "/Volumes/Extended-1TB/Sony_Test_Sandbox"

def verify_directionality():
    files = sorted([os.path.join(FOLDER, f) for f in os.listdir(FOLDER) if f.lower().endswith(SUPPORTED_EXTENSIONS)])[:30]
    
    fft_dirs = []
    struct_dirs = []
    
    print(f"Versus Benchmarking: FFT Anisotropy vs Structure Tensor on {len(files)} images...")
    
    for path in tqdm(files):
        try:
            with rawpy.imread(path) as raw:
                rgb = raw.postprocess(use_camera_wb=True, demosaic_algorithm=rawpy.DemosaicAlgorithm.PPG, half_size=False)
            gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
            h, w = gray.shape
            
            # 1. FFT Directionality (Baseline)
            # (Simplified from analyzer.py)
            f = scipy.fft.fft2(gray)
            fshift = scipy.fft.fftshift(f)
            mag = np.abs(fshift)
            # Mask
            cy, cx = h / 2.0, w / 2.0
            r_outer = min(h, w) * 0.4
            r_inner = min(h, w) * 0.1
            y, x = np.ogrid[:h, :w]
            dist = np.sqrt((x - cx)**2 + (y - cy)**2)
            mask = (dist >= r_inner) & (dist <= r_outer)
            
            hf_energy = mag[mask]
            # Moments
            rel_y = (np.arange(h) - cy)
            rel_x = (np.arange(w) - cx)
            y_coords = rel_y.reshape(-1, 1).repeat(w, axis=1)[mask]
            x_coords = rel_x.reshape(1, -1).repeat(h, axis=0)[mask]
            
            m00 = np.sum(hf_energy)
            m01 = np.sum(y_coords * hf_energy)
            m10 = np.sum(x_coords * hf_energy)
            mu20 = np.sum((x_coords - (m10/m00))**2 * hf_energy) / m00
            mu02 = np.sum((y_coords - (m01/m00))**2 * hf_energy) / m00
            mu11 = np.sum((x_coords - (m10/m00)) * (y_coords - (m01/m00)) * hf_energy) / m00
            
            common = np.sqrt(((mu20 - mu02)/2)**2 + mu11**2 + 1e-9)
            lam1 = (mu20 + mu02) / 2 + common
            lam2 = (mu20 + mu02) / 2 - common
            fft_dir = 1.0 - (lam2 / (lam1 + 1e-9))
            fft_dirs.append(fft_dir)
            
            # 2. Structure Tensor Directionality (Candidate)
            gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            
            # Structure Tensor J = [[sum(Igx^2), sum(Igx*Igy)], [sum(Igx*Igy), sum(Igy^2)]]
            # We can sum over the whole image or blocks?
            # Let's sum over the whole image for global directionality/shake
            Jxx = np.sum(gx * gx)
            Jyy = np.sum(gy * gy)
            Jxy = np.sum(gx * gy)
            
            # Eigenvalues of 2x2 matrix
            # Trace = lam1 + lam2 = Jxx + Jyy
            # Det = lam1 * lam2 = Jxx*Jyy - Jxy*Jxy
            # lam = (Trace +/- sqrt(Trace^2 - 4*Det)) / 2
            
            trace = Jxx + Jyy
            det = Jxx * Jyy - Jxy * Jxy
            
            delta = np.sqrt(trace*trace - 4*det)
            l1 = (trace + delta) / 2
            l2 = (trace - delta) / 2
            
            # Directionality aka Coherence
            # If l1 >> l2, highly directional (linear motion blur? Or just strong edges?)
            # Wait. Motion blur causes LOSS of high freq in one direction.
            # So the gradients in the direction of motion are LOW.
            # The gradients perpendicular to motion are HIGH.
            # So highly directional gradients -> Motion Blur?
            # Coherence = (l1 - l2) / (l1 + l2)
            struct_dir = (l1 - l2) / (l1 + l2 + 1e-9)
            struct_dirs.append(struct_dir)
            
        except Exception as e:
            print(f"Error {path}: {e}")

    tau, _ = scipy.stats.kendalltau(fft_dirs, struct_dirs)
    pearson, _ = scipy.stats.pearsonr(fft_dirs, struct_dirs)
    
    print("\n📈 Correlation Results (Structure Tensor vs FFT Directionality):")
    print(f"   Kendall's Tau: {tau:.4f}")
    print(f"   Pearson: {pearson:.4f}")

if __name__ == "__main__":
    verify_directionality()
