#include <stdio.h>
#include <curl/curl.h>

// This function will be called to write the response data
size_t write_data(void *buffer, size_t size, size_t nmemb, void *userp) {
    return size * nmemb;  // return the number of bytes processed
}

long http_get(const char *url) {
    long http_code = 0;
    CURL *curl;
    CURLcode res;

    curl = curl_easy_init();
    if(curl) {
        curl_easy_setopt(curl, CURLOPT_URL, url);

        // Set the write function and data destination for curl
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_data);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, NULL);  // NULL means discard the data

        res = curl_easy_perform(curl);
        if(res != CURLE_OK)
            fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));
        else
            curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &http_code);
        curl_easy_cleanup(curl);
    }
    return http_code;
}
