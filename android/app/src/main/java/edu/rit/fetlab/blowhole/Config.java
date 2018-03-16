package edu.rit.fetlab.blowhole;

/**
 * The configuration constants
 */
public class Config {

    /**
     * The threshold to consider a blow
     */
    public static final int THRESHOLD = 500;

    /**
     * The threshold for a blow
     */
    public static final float CHUNK_LENGTH = 0.5f;

    /**
     * The minimum blow length (in seconds)
     */
    public static final float MIN_BLOW_LENGTH = 0.7f;

    /**
     * The sampling rate (in hertz)
     */
    public static final int RATE = 8000;

    /**
     * The coefficients. Used to identify the radius given a frequency
     */
    public static final double[][] COEFFICIENTS = {
            {3.41509687e+01, -1.37476056e-03, 5.26842343e+00},      // R = 2.5mm
            {2.70604893e+01, -1.24424194e-03, 4.60348707e+00},      // R = 5mm
            {2.61214046e+01, -1.40655500e-03, 4.45459190e+00}       // R = 10mm
    };

    /**
     * The window size (for the FFT)
     */
    public final static float WINDOW_SIZE = 0.1f;




}
