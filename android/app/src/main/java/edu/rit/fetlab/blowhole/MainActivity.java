package edu.rit.fetlab.blowhole;

import android.Manifest;
import android.app.Activity;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.util.Log;
import android.widget.Button;
import android.widget.RadioButton;
import android.widget.TextView;
import android.widget.Toast;

import butterknife.BindView;
import butterknife.ButterKnife;
import butterknife.OnClick;
import permissions.dispatcher.NeedsPermission;
import permissions.dispatcher.OnPermissionDenied;
import permissions.dispatcher.RuntimePermissions;

/**
 * Android Main Activity
 */
@RuntimePermissions
public class MainActivity extends Activity {

    @BindView(R.id.btnStartListening) Button btnStart;
    @BindView(R.id.btnStopListening) Button btnStop;
    @BindView(R.id.tvInfo) TextView tvInfo;



    /**
     * Message Handler.
     */
    private Handler handler = new Handler() {
        @Override
        public void handleMessage(Message message) {
            if (message.what == Messages.RECOGNIZED_BLOW) {
                Log.d("Logging:", message.toString());
                int i = (int) Float.parseFloat(message.obj.toString());
                tvInfo.setText(Data.query_cell( i ).split("\t")[0] );
            }
        }
    };

    MicStream m = new MicStream(handler);


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        ButterKnife.bind(this);

        Data.init();

    }


    public Selection getSelectedOption() {
        return Selection.ANIMAL_CELL; // default
    }


    /**
     * Start listening for blows.
     */
    @NeedsPermission(Manifest.permission.RECORD_AUDIO)
    @OnClick(R.id.btnStartListening)
    public void listen() {
        btnStart.setEnabled(false);
        m.start();
    }

    /**
     * Stop listening
     */
    @OnClick(R.id.btnStopListening)
    public void stop() {
        MainActivityPermissionsDispatcher.listenWithCheck(this);
        btnStart.setEnabled(true);
        m.interrupt();
    }

    @OnPermissionDenied(Manifest.permission.RECORD_AUDIO)
    void showDeniedRecordAudio() {
        Toast.makeText(this, R.string.record_audio_denied, Toast.LENGTH_SHORT).show();
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        MainActivityPermissionsDispatcher.onRequestPermissionsResult(this, requestCode, grantResults);
    }




}
