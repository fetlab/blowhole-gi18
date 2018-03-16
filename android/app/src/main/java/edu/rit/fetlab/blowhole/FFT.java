package edu.rit.fetlab.blowhole;

import org.jtransforms.fft.DoubleFFT_1D;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/**
 * A Fast Fourier Transform wrapper for jTransforms to provide similar functionality to numpy.fft
 * functions used by the Blowhole Python implementation.
 */
public class FFT {

    /**
     * Compute the fast fourier transform
     * @param raw the raw signal
     * @return the computed fast fourier transform
     */
    public static double[] fft(double[] raw) {
        double[] in = raw;
        DoubleFFT_1D fft = new DoubleFFT_1D(in.length);
        fft.realForward(in);
        return in;
    }
    /**
     * Computes the physical layout of the fast fourier transform.
     * See jTransform documentation for more information.
     * http://incanter.org/docs/parallelcolt/api/edu/emory/mathcs/jtransforms/fft/DoubleFFT_1D.html#realForward(double[])
     * @param fft the fast fourier transform
     * @param re  the real part fo the fast fourier transform
     * @param im  the imaginary part of the fast fourier transform
     */
    public static void rfft(double[] fft, double[] re, double[] im) {
        int n = fft.length;
        if (n % 2 == 0) {
            // n is even
            for (int i = 0; i < n/2; i++) {
                re[i] = fft[2*i];
                im[i] = fft[2*i+1];
            }
            im[0] = 0;
            re[n/2] = fft[1];
        } else {
            // n is odd
            for (int i = 0; i < n/2; i++) {
                re[i] = fft[ 2*i ];
                im[i] = fft[ 2*i+1 ];
            }
            im[0] = 0;
            im[(n-1)/2] = fft[1];

        }
    }

    /**
     * Returns the Discrete Fourier Transform sample frequencies.
     * See numpy.fft.rfftfreq for more information.
     * @param n Window length
     * @param d Sample spacing
     * @return Array of length n + 1 containing the sample frequencies
     */
    public static double[] rfftfreq(int n, double d) {
        double val = 1.0 / (n * d);
        int N = n / 2 + 1;
        double[] results = new double[N];
        for (int i = 0; i < N; i++) {
            results[i] = i * val;
        }
        return results;
    }

    /**
     * Window the array in WINDOW_SIZE chunks.
     * @param fft the array to be windowed
     * @return a windowed array
     */
    public static List<int[]> windowChunks(int[] fft) {

        int windowSize = (int) (Config.WINDOW_SIZE * Config.RATE);
        int numWindow = fft.length / windowSize;
        List<int[ ]> ffts = new ArrayList<>();

        for (int x = 0; x < numWindow; x++) {
            final int start = x * windowSize;
            final int end = (x + 1) * windowSize;
            int[ ] f = Arrays.copyOfRange(fft, start, end);
            ffts.add(f);
        }
        return ffts;
    }

}
