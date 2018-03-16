package edu.rit.fetlab.blowhole;

import android.media.AudioFormat;
import android.media.AudioRecord;
import android.media.MediaRecorder;
import android.os.Handler;
import android.os.Process;
import android.util.Log;

import org.apache.commons.math3.stat.descriptive.DescriptiveStatistics;
import org.jtransforms.fft.DoubleFFT_1D;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import static edu.rit.fetlab.blowhole.FFT.rfftfreq;
import static edu.rit.fetlab.blowhole.FFT.rfft;
import static edu.rit.fetlab.blowhole.Util.abs;
import static edu.rit.fetlab.blowhole.Util.roundEven;
import static edu.rit.fetlab.blowhole.Util.short2int;

/**
 * Blow processing and recognition.
 */
public class MicStream extends Thread {


    /**
     * The message handler
     */
    private Handler handler;

    /**
     * The chunk buffer.
     */
    private static List<Integer> _chunkBuffer = new ArrayList<>();

    /**
     * The selected object
     */
    private Selection selection;

    /**
     * Class constructor
     * @param handler the message handler
     */
    public MicStream(Handler handler) {
        this.handler = handler;
    }

    /**
     * Used for logging
     */
    private final String TAG = getClass().getName();

    /**
     * Class constructor
     * @param handler   the message handler
     * @param selection the selected object
     */
    public MicStream(Handler handler, Selection selection) {
        this.handler = handler;
        this.selection = selection;
    }

    /**
     * Listen for blow and identify the radius on a thread.
     */
    @Override
    public void run() {

        android.os.Process.setThreadPriority(Process.THREAD_PRIORITY_URGENT_AUDIO);

        // The minimum buffer size for the device
        int minBufferSize = AudioRecord.getMinBufferSize(Config.RATE, AudioFormat.CHANNEL_IN_MONO,
                            AudioFormat.ENCODING_PCM_16BIT);

        int bufferSize = (int) ( Config.RATE * Config.CHUNK_LENGTH );

        AudioRecord ar = new AudioRecord(   MediaRecorder.AudioSource.MIC,
                                            Config.RATE,
                                            AudioFormat.CHANNEL_IN_MONO,
                                            AudioFormat.ENCODING_PCM_16BIT,
                                            bufferSize);

        ar.startRecording();

        Log.d(TAG, "Started recording");

        while (!interrupted()) {

            short[] buffer = new short[bufferSize];
            int read = ar.read(buffer, 0, bufferSize);

            short[] r = Arrays.copyOfRange(buffer, 0, read);

            int[] s2i = short2int(r);
            getBlow(s2i, handler);
        }

        Log.d(TAG, "Stopped recording");

        ar.release();

    }

    /**
     * Get the blow from a chunk.
     * @param chunk a chunk
     * @param handler the message handler
     */
    private static void getBlow(int[] chunk, Handler handler) {
        if (_chunkBuffer.size() >= Config.RATE * Config.MIN_BLOW_LENGTH) {
            float result = identifyBlow(_chunkBuffer);
            Log.d("MicStream", "Identified: " + result);

            handler.obtainMessage(Messages.RECOGNIZED_BLOW, result).sendToTarget();

        }

        for (int[] f : FFT.windowChunks(chunk)) {
            double rms = Util.getRootMeanSquare(f);

            if (rms > Config.THRESHOLD) {
                for (int item : f) {
                    _chunkBuffer.add(item);
                }
            } else {
                _chunkBuffer = new ArrayList<>();
            }
        }
    }

    /**
     * Identify the radius given the blow
     * @param raw a blow chunk
     * @return the radius
     */
    private static float identifyBlow(List<Integer> raw) {
        int[] array = raw.stream().mapToInt(i->i).toArray();
        // log.info("size: " + array.length);


        List<Double> wFreqs = new ArrayList<>();
        for (int[ ] chunks : FFT.windowChunks(array)) {
            DoubleFFT_1D fft = new DoubleFFT_1D(chunks.length);
            double[] dbl = Arrays.stream(chunks).mapToDouble(i->i).toArray();
            fft.realForward(dbl);
            double[] re = new double[dbl.length/2 + 1];
            double[] im = new double[dbl.length/2 + 1];
            rfft(dbl, re, im);

            double[ ] v  = abs(re, im);

            //  get the max index
            double max = 0;
            double maxId = 0;
            for (int i = 0; i < v.length; i++) {
                if (v[i] > max) {
                    max = v[i];
                    maxId = i;
                }
            }


            double[] results = rfftfreq(chunks.length, 1.0/Config.RATE);

            wFreqs.add(results[(int) maxId]);
        }

        DescriptiveStatistics statistics = new DescriptiveStatistics();
        wFreqs.stream().forEach(statistics::addValue);
        double freq = Math.round(statistics.getPercentile(50) * 100d) / 100d;



        double[] tmp_freqs = rfftfreq(raw.size(), 1.0/Config.RATE);

        double[] blow = raw.stream().mapToDouble(i->i).toArray();
        DoubleFFT_1D fft = new DoubleFFT_1D(blow.length);
        fft.realForward(blow);
        double[] re = new double[blow.length/2 + 1];
        double[] im = new double[blow.length/2 + 1];
        rfft(blow, re, im);
        double[] absolute = abs(re, im);


        double max = 0;
        int maxId = 0;
        for (int i = 0 ; i < absolute.length; i ++)
        {
            if (absolute[i] > max) {
                max = absolute[i];
                maxId = i;
            }
        }

        double blow_freq = tmp_freqs[maxId];


        if (Math.abs(blow_freq - freq) > 100) {
            return -1.0f;
        }


        // r := f(x) = A * e^Bx + C
        // COEFFICIENTS[i][ ] = 0: 2.5mm, 1: 5mm, 2: 10mm
        double radius = Config.COEFFICIENTS[1][0] * Math.pow(( Math.exp(1)), Config.COEFFICIENTS[1][1] * freq) + Config.COEFFICIENTS[1][2];

        Log.d("MicStream", String.format("Frequency: %.2fHz", freq));
        Log.d("MicStream", String.format("Radius: %.0f", roundEven(radius)));


        _chunkBuffer = new ArrayList<>();

        return (float) roundEven(radius);
    }
}
