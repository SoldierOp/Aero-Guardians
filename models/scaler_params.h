// Scaler parameters for ESP32 preprocessing

const int FEATURE_COUNT = 8;

const char* FEATURE_NAMES[] = {
  "voc",
  "pm25",
  "pm10",
  "dust",
  "temperature",
  "humidity",
  "water_level",
  "tds",
};

const float FEATURE_MEAN[] = {
  519.509824f,
  50.168050f,
  80.208727f,
  72.536147f,
  29.243524f,
  43.870415f,
  123.331116f,
  931.947239f,
};

const float FEATURE_STD[] = {
  249.008209f,
  31.420369f,
  51.791469f,
  49.306110f,
  3.366241f,
  4.736659f,
  22.750872f,
  151.308508f,
};
