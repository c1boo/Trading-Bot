def bb_check_long(data_row, bb_lower_band):
    close_price = data_row["Close"]
    if bb_lower_band > close_price:
        return True

    return False


def stoch1_check_long(stochrsi_k):
    if stochrsi_k <= 0.1:
        return True
    return False


def rsi_check_long(rsi_value):
    if rsi_value < 30:
        return True
    return False


def stoch2_check_long(stoch2_k, stoch2_d):
    prev_k = stoch2_k.iloc[0]
    prev_d = stoch2_d.iloc[0]
    for i in range(1, len(stoch2_k)):
        k = stoch2_k.iloc[i]
        d = stoch2_d.iloc[i]
        if prev_k < 10 and prev_d < 10 and k < 10 and d < 10:
            # IF CROSS HAPPENED BETWEEN K AND D SIGNALS UNDER 10 VALUE
            if prev_k < prev_d and k >= d:
                return True

        prev_k = k
        prev_d = d

    return False


def trix_check_long(trix_value):
    if trix_value < 0:
        return True
    return False


def cci_check_long(cci_data):
    down_trend = False
    for value in cci_data:
        if value < -90:
            down_trend = True
        elif down_trend:
            return True

    return False


def macd_check_long(macd_ind, macd_signal):
    above_threshold = 0
    below_threshold = 0
    for i in range(len(macd_ind)):
        indicator = macd_ind.iloc[i]
        signal = macd_signal.iloc[i]
        if indicator < 0 and signal < 0:
            if indicator < signal:
                below_threshold += 1
        else:
            above_threshold += 1

    if below_threshold > above_threshold:
        return True
    return False


def william_r_check_long(william_r):
    first_cross = second_cross = third_cross = final_cross = False
    slicer_index = 0
    data_length = len(william_r)
    for index in range(slicer_index, data_length):
        value = william_r.iloc[index]
        if value < -90:
            first_cross = True
            slicer_index = index
            break

    for index in range(slicer_index, data_length):
        value = william_r.iloc[index]
        if -70 > value > -90:
            second_cross = True
            slicer_index = index
            break

    for index in range(slicer_index, data_length):
        value = william_r.iloc[index]
        if value < -90:
            third_cross = True
            slicer_index = index
            break

    for index in range(slicer_index, data_length):
        value = william_r.iloc[index]
        if value > -70:
            final_cross = True
            break

    return first_cross and second_cross and third_cross and final_cross


def adx_check_long(adx_data):
    trend_breaker = 0.16
    prev_value = adx_data.iloc[0]
    for value in adx_data.iloc[1:]:
        if trend_breaker > value - prev_value:
            return True
        prev_value = value

    return False


def check_long_buy(last_10_data, last_10_indicators):
    bollinger_band_result = stoch1_result = rsi_result = trix_result = False
    for i in range(len(last_10_data)):
        indicator = last_10_indicators.iloc[i]
        if not bollinger_band_result:
            bollinger_band_result = bb_check_long(last_10_data.iloc[i], indicator["Bollinger Band Low"])
        if not stoch1_result:
            stoch1_result = stoch1_check_long(indicator["Stochastics RSI 1 K"])
        if not rsi_result:
            rsi_result = rsi_check_long(indicator["RSI"])
        if not trix_result:
            trix_result = trix_check_long(indicator["TRIX"])

    stoch2_result = stoch2_check_long(last_10_indicators["Stochastics RSI 2 K"],
                                      last_10_indicators["Stochastics RSI 2 D"])
    cci_result = cci_check_long(last_10_indicators["CCI"])
    macd_result = macd_check_long(last_10_indicators["MACD IND"], last_10_indicators["MACD SIGNAL"])
    william_result = william_r_check_long(last_10_indicators["Williams RSI"])
    adx_result = adx_check_long(last_10_indicators["ADX"])

    return bollinger_band_result and stoch1_result and rsi_result and trix_result and \
        stoch2_result and cci_result and macd_result and william_result and adx_result
