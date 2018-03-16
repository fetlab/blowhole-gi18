package edu.rit.fetlab.blowhole;

import java.util.Locale;


/**
 * Ported helper functionality from Blowhole Python implementation
 */
public class Util {

    /**
     * Calculates the absolute value of a complex input. The absolute value of a+ib is sqrt(a^2+b^2)
     * @param re The real part of the complex input
     * @param im The imaginary part of the complex input
     * @return The absolute value of the complex input
     */
    public static double[] abs(double[] re, double[] im) {
        double[] result = new double[re.length];
        for (int i = 0; i < result.length; i++) {
            result[i] = Math.sqrt(re[i]*re[i] + im[i]*im[i]);
        }
        return result;
    }

    /**
     * Calculates the root mean square of the array
     * @param window the array
     * @return the root mean square of the array
     */
    public static double getRootMeanSquare(int[] window) {
        double x = 0;
        for (int w : window) {
            x += Math.pow(w, 2);
        }
        return Math.sqrt(x / window.length);
    }

    public static double roundEven(double n) {
        return 2 * Math.round(n/2);
    }

    /**
     * Converts a short array to an int array
     * @param s a short array
     * @return the resulting int array
     */
    public static int[] short2int(short[] s) {
        int[] x = new int[s.length];
        for (int i = 0; i < s.length; i++ ) {
            x[i] = s[i];
        }
        return x;
    }
    /**
     * Prints an array
     * @param array the input array
     * @return the string representation of the array
     */
    public static String printArray(int[] array) {
        if (array.length < 6) {
            StringBuilder s = new StringBuilder();
            s.append("[");
            for (int item : array) {
                s.append(item + ", ");
            }
            s.append("\b\b]");
            return s.toString();
        } else {
            return String.format(Locale.US, "[%d, %d, %d, ..., %d, %d, %d]",
                    array[0], array[1], array[2],
                    array[array.length - 3],
                    array[array.length - 2],
                    array[array.length - 1]);
        }
    }

    /**
     * Prints an array
     * @param array the input array
     * @return the string representation of the array
     */
    public static String printArray(double[] array) {
        if (array.length < 6) {
            StringBuilder s = new StringBuilder();
            s.append("[");
            for (double item : array) {
                s.append(item + ", ");
            }
            s.append("\b\b]");
            return s.toString();
        } else {
            return String.format(Locale.US, "[%f, %f, %f, ..., %f, %f, %f]",
                    array[0], array[1], array[2],
                    array[array.length - 3],
                    array[array.length - 2],
                    array[array.length - 1]);
        }
    }


}
