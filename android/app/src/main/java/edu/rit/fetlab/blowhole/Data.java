package edu.rit.fetlab.blowhole;

import android.util.Log;

import java.util.HashMap;

/**
 * Data is a class to hold the information about the objects.
 * TODO: Replace the Data class with a JSON document
 */
public class Data {

    /**
     * Globe
     */
    private static HashMap<Integer, String> g = new HashMap<>();

    /**
     * Animal Cell
     */
    private static HashMap<Integer, String[]> c = new HashMap<>();


    /**
     * Initialize the HashMap
     */
    public static void init() {
        g.put(6, "North America");
        g.put(8, "Africa");
        g.put(10, "Australia");
        g.put(12, "South America");
        g.put(14, "Eurasia");

        c.put(6, new String[]{"Mitochondria", "Mitochondria are rod-shaped organelles that can be " +
                "considered the power generators of the cell, converting oxygen and nutrients into adenosine triphosphate (ATP)"});
        c.put(8, new String[]{"Nucleoulus", "Small dense spherical structure in the nucleus of a cell during interphase."});
        c.put(4, new String[]{"Golgi Apparatus", "The Golgi apparatus gathers simple molecules and combines them to make molecules that are more complex"});
        c.put(12, new String[]{"Endoplasmic Reticulum", "A network of membranous tubules within the cytoplasm of a eukaryotic cell, continuous with the nuclear membrane."});
        c.put(10, new String[]{"Centrosome", "An organelle near the nucleus of a cell that contains the centrioles and from which the spindle fibers develop in cell division."});
    }

    /**
     * Get the continent given a radius
     * @param i the radius
     * @return the continent
     */
    public static String query_world(int i) {

        Log.d("myTag", "Received: " + i);

        String s = g.get(i);

        Log.d("MyTag", "Returning: " + s);

        if (s == null) return Messages.RADIUS_NOT_FOUND;

        return s;
    }

    /**
     * Get the name and description of the part of the cell given a radius
     * @param i the radius
     * @return the name and the description of the part of the cell. The string is separated using
     * tabs
     */
    public static String query_cell(int i) {

        Log.d("Data", "Received" + "i");
        String[] s = c.get(i);

        Log.d("MyTag", "Returning: " + s);

        if (s == null) return Messages.RADIUS_NOT_FOUND;

        return s[0] + "\t" + s[1];

    }

}
