package com.allenzby.lotterydraw;

import android.app.Activity;
import android.graphics.Color;
import android.os.Bundle;
import android.view.View;
import android.view.Window;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public class MainActivity extends Activity {

    private WebView web;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // 状态栏 / 导航栏配色与界面一致
        Window w = getWindow();
        w.setStatusBarColor(Color.parseColor("#1D3FD0"));
        w.setNavigationBarColor(Color.parseColor("#F4F6FB"));

        web = new WebView(this);
        web.setBackgroundColor(Color.parseColor("#F4F6FB"));

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);          // 设置项保存在 localStorage
        s.setSupportZoom(false);
        s.setBuiltInZoomControls(false);
        s.setDisplayZoomControls(false);
        s.setTextZoom(100);                    // 避免系统字体放大导致布局错乱
        s.setAllowFileAccess(true);
        s.setCacheMode(WebSettings.LOAD_NO_CACHE);

        web.setWebViewClient(new WebViewClient());
        web.setOverScrollMode(View.OVER_SCROLL_NEVER);
        web.loadUrl("file:///android_asset/index.html");

        setContentView(web);
    }

    @Override
    public void onBackPressed() {
        if (web != null && web.canGoBack()) {
            web.goBack();
        } else {
            super.onBackPressed();
        }
    }

    @Override
    protected void onDestroy() {
        if (web != null) {
            web.destroy();
            web = null;
        }
        super.onDestroy();
    }
}
