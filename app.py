import time
import pandas as pd
import streamlit as st
from forex_python.converter import CurrencyRates
#own helping module
from HelpingFunctions import AboutSection
from HelpingFunctions import Conclusion
from HelpingFunctions import displaydisclaimer
from HelpingFunctions import WelcomeNote
from HelpingFunctions import companyticker
from HelpingFunctions import futuretrend
from HelpingFunctions import DataLoad
from HelpingFunctions import pastbargraph
from HelpingFunctions import performancegraph
from HelpingFunctions import predictedtrend
from HelpingFunctions import trend
# from HelpingFunctions import load_data

#own predicton module
from prediction import Forecast
from prediction import ForecastDataFrame
from prediction import PastDataFrame


#page title
st.title("Stock Prediction")

#initialization
companies = None
company_names = None
# currencyrate = 1

#sidebar
with st.sidebar as sbar:
    indian_cbox = st.checkbox(label="Indian Companies", key="indian_cbox")
    foreign_cbox = st.checkbox(label="Foreign Companies", key="foreign_cbox")

    if indian_cbox == True and foreign_cbox == False:
        companies = companyticker("Indian Companies")
        company_names = companies["name"].tolist()

    elif foreign_cbox == True and indian_cbox == False:
        companies = companyticker("Foreign Companies")
        company_names = companies["name"].tolist()

    elif indian_cbox == True and foreign_cbox == True:
        companies = companyticker(all_comp=True)
        company_names = companies["name"].tolist()


    try:
        company_names.insert(0, " ")
        selected_comp = st.selectbox(label="Company name here.", options=company_names)

    except:
        st.info("Please select an option first")
        selected_comp = " "

    #search button
    st.button("Search", key="search_btm", use_container_width=True)

    if companies is not None:
        st.markdown(f"<h1 style ='text-align: center; color: green'>{len(companies)}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h4 style ='text-align: center'>Companies Available ", unsafe_allow_html=True)
    #radio button
    currency_radio = st.radio(label = "Choose Currency", options = ["INR" , "USD"])


# initialization
data = None
past_data = None
current_date =  pd.to_datetime("today").date()

in_inr = True
in_usd = False

if selected_comp != " ":

    # load data
    cls_obj = DataLoad()

    data = cls_obj.load_data(tickertbl=companies, company=selected_comp)

    print("___________________________________Original ___________________________________")
    print(data)

    if data is not None :
        if len(data.columns) > 7:
            st.warning("This company is delisted from NSE or the name has been changed.")
            data = None
            selected_comp = " "
        else:
            # update the currency rate to USD
            if currency_radio == "INR":
                currency_rate = cls_obj.currencyrate(convert_to = "INR")
                in_inr = True
                in_usd = False

            else:
                currency_rate = cls_obj.currencyrate(convert_to= "USD")
                in_inr = False
                in_usd = True

            data[['Open', 'High', 'Low', 'Close', 'Adj Close']] = data[ ['Open', 'High', 'Low', 'Close','Adj Close']] * currency_rate

            # converting currency to USD

    #creating layout for page
    tab1, tab2, tab3, tab4 = st.tabs(["Details", "Forecast", "Performance", "About"])

    with tab1:
        if data is not None:
            # currency conversion
            try:
                #start date user input
                start_date = st.text_input(label="Start Date", value=min(data["Date"].dt.strftime("%Y-%m-%d")))
                start_date = pd.to_datetime(start_date)
                #end date user input
                end_date = st.text_input(label="End Date", value=max(data["Date"].dt.strftime("%Y-%m-%d")))
                end_date = pd.to_datetime(end_date)

            except:
                st.warning("Invalid date format. The Date should be in this format YYYY-MM-DD .")

                start_date = min(data["Date"])
                end_date = max(data["Date"])

            if end_date <= start_date:
                # display a warning message if user enters a end_date which is less than the start_date.
                st.warning("Start Date should be before the end date.")

            else:
                # filter the table based on the date range specified by the user.
                filterdata = data[(data["Date"] >= start_date) & (data["Date"] <= end_date)]

                heading_2 = "<h4 style='color :blue ; text-align: center;'>Stock Closing</h4>"
                st.markdown(heading_2, unsafe_allow_html=True)

                #past: actual trend
                trendline = trend(filterdata, "Close", startdate=start_date, enddate=end_date)


                start_string = start_date.strftime(format="%Y-%m-%d") #start date string
                end_string = end_date.strftime(format="%Y-%m-%d")  #end date string

                sub_head1 = "<p style = 'text-align:center'><b>Trend from {} to {}</b></p>".format(start_string,
                                                                                                   end_string)
                st.markdown(sub_head1, unsafe_allow_html=True)
                st.pyplot(trendline)

                st.markdown("<br>", unsafe_allow_html=True)

                #dataframe with past actual and predicted close stock price
                data_in_usd = data.copy()
                if in_usd == True:
                    pass
                else:
                    curr_to_usd = cls_obj.currencyrate(convert_to="USD")
                    data_in_usd[['Open', 'High', 'Low', 'Close', 'Adj Close']] = data_in_usd[
                                                                                 ['Open', 'High', 'Low', 'Close',
                                                                                  'Adj Close']] * curr_to_usd

                past_data = PastDataFrame(data_in_usd)
                print("                               BEfore                      ")
                print(past_data)


                #past: predicted trend

                #currency as per user want
                if currency_radio == "USD" :
                    pass
                else:
                    usd_to_inr =  CurrencyRates().get_rate("USD" , "INR")
                    past_data[["Actual", "Predictions"]] = past_data[["Actual", "Predictions"]] * usd_to_inr
                    print("++++++++++++++++++++++++++++++After+++++++++++++++++++++++")
                    print(past_data)


                past_prediction_trend = predictedtrend(past_data, startdate=start_date, enddate=end_date)
                sub_head3 = "<h4 style = 'text-align: center;'>Actual VS Prediction</h4>"
                st.markdown(sub_head3, unsafe_allow_html=True)
                st.pyplot(past_prediction_trend)

                st.markdown("<br>", unsafe_allow_html=True)

                st.markdown("<h4 style = 'text-align: center;'>Bar Graph</h4>", unsafe_allow_html=True)
                st.markdown("<h6 style = 'text-align: center;'>({} : {})</h6>".format(start_string, end_string),
                            unsafe_allow_html=True)


                pbar = pastbargraph(past_df = past_data, startdate = start_date, enddate=end_date)
                st.pyplot(pbar)

        else:
            st.info("Either data For this company is not available or there was some connection issue you can , Sorry for the inconvenience, please try again.")

# future prediction
futuredf = None

if selected_comp != " ":
    with tab2:
        toggle = st.toggle(label="Forecast", key="toggle_1")
        if toggle == True:

            #display disclaimer  for future prediction
            displaydisclaimer()
            chck_box1 = st.checkbox(label="I Understand, Please Continue.")

            if chck_box1 == True:
                st.info("Thank you for your understanding and responsible use of our stock prediction tool. ")
                st.markdown("<hr>", unsafe_allow_html=True)

                sub_head4 = "<h4 style = 'text-align:center'>Today's Overview</h4>"
                st.markdown(sub_head4, unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

                # layout
                col1, col2, col3, col4 ,col5= st.columns(5)

                # fetch today's(current day) data
                current_price ,today_open_price, today_high_price = cls_obj.todaysinfo()

                if currency_radio == "USD":
                    pass
                else:
                    currate = CurrencyRates().get_rate("USD", "INR")
                    current_price = current_price * currate
                    today_open_price = today_open_price * currate
                    print("=======", today_high_price , "*" , currate)
                    today_high_price = today_high_price * currate
                with col1:

                    st.markdown("<h6  style = 'text-align:center'>Today's Date </h6>", unsafe_allow_html=True)
                    st.markdown("<p  style =  'text-align:center; color:blue;'>{}</p>".format(current_date), unsafe_allow_html=True)

                with col2:

                    st.markdown("<h6  style = 'text-align:center'>Open Price</h6>", unsafe_allow_html=True)
                    st.markdown("<p  style = 'text-align:center ; color:blue;'>{}</p>".format(today_open_price), unsafe_allow_html=True)

                with col3:
                    st.markdown("<h6  style = 'text-align:center'>High Price</h6>", unsafe_allow_html=True)
                    st.markdown("<p  style = 'text-align:center ; color:blue;'>{}</p>".format(today_high_price), unsafe_allow_html=True)
                with col4:
                    # current_day_open =data[data["Date"] == pd.to_datetime("today").date()]["Open"].round(2).to_string(index=False)
                    st.markdown("<h6  style = 'text-align:center'>Current Price</h6>", unsafe_allow_html=True)
                    st.markdown("<p  style = 'text-align:center ; color:blue;'>{}</p>".format(current_price), unsafe_allow_html=True)

                with col5:
                    st.markdown("<h6 style = 'text-align:center '>Close Price (predicted)</h6>", unsafe_allow_html=True)
                    current_day_predicted = Forecast(data, future_days=0)
                    current_day_predicted = round(current_day_predicted[0], 2)

                    st.markdown("<p style = 'text-align:center ; color:lightgreen;'>{}</p>".format(current_day_predicted),
                                unsafe_allow_html=True)

                st.markdown("<hr>", unsafe_allow_html=True)
                st.markdown("<h4 style = 'text-align:center'>Future Prediction</h4>", unsafe_allow_html=True)
                st.markdown("<p style = 'text-align:center'>Specify for next how many days you want to predict:</p>",
                            unsafe_allow_html=True)


                # future prediction

                #layout
                col1, col2, col3 = st.columns(3)
                with col1:
                    user_input_days = st.number_input(label="Days", max_value=365, value=1)  # taking user input

                with col2:
                    st.markdown("<h5 style = 'text-align:center'>Today</h5>", unsafe_allow_html=True)
                    st.markdown("<p style = 'text-align: center'>{}</p>".format(current_date), unsafe_allow_html=True)

                with col3:
                    st.markdown("<h5 style = 'text-align:center'>Next Date</h5>", unsafe_allow_html=True)
                    next_date = current_date + pd.Timedelta(days=user_input_days)
                    st.markdown("<p style = 'text-align: center'>{}</p>".format(next_date), unsafe_allow_html=True)

                #currency in USD for future data frame also

                future = Forecast(dataframe= data_in_usd, future_days=user_input_days)
                futuredf = ForecastDataFrame(predicted_values = future, future_days=user_input_days)

                #currency as per user want
                if currency_radio == "USD":
                    pass
                else:
                    usd_to_inr = CurrencyRates().get_rate("USD", "INR")
                    futuredf["Predictions"] =  futuredf["Predictions"] * usd_to_inr


                # future / forecast  graph
                future_trend = futuretrend(futuredf=futuredf, currentdf= data)
                st.pyplot(future_trend)

                # display future / forecast table
                displaytbl = futuredf.copy()
                displaytbl["Date"] = displaytbl["Date"].dt.date

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("<h5 style = 'text-align:center'>Forecast Table</h5>", unsafe_allow_html=True)

                st.markdown("<p> The table shows the next {} days predicted stock price.<p>".format(user_input_days),
                            unsafe_allow_html=True)

                st.dataframe(displaytbl,
                             use_container_width=True)  # display from next 1 day i.e excluding current day data

# performance area
if selected_comp != " ":

    with tab3:
        if st.session_state.get("toggle_1") == False:
            st.info("Please first read the disclaimer in the forecast section.")

        else:

            st.markdown('<h5>• Wanna see how our model performed yesterday ?</h5>', unsafe_allow_html=True)
            st.markdown('<hr>', unsafe_allow_html=True)
            st.markdown("<h5 style = 'text-align:center'>Yesterday</h5>", unsafe_allow_html=True)

            if (current_date - data.iloc[-1]["Date"].date()).days > 1:
                st.info("Showing result for {} as market was closed yesterday.".format(data.iloc[-1]["Date"].date().strftime("%Y-%m-%d")))

            # layout
            col1, col2 = st.columns(2)

            with col1:
                #yesterday date

                previous_day1_date = data.iloc[-1]["Date"].date()

                #yesterday data
                previous_day1 = past_data[past_data["Date"].dt.date == previous_day1_date]  # str(round(past_data[-1:],4))

                st.markdown("<h6 style = 'text-align:center'> Predicted</h6>", unsafe_allow_html=True)

                #yesterdaty predicted price
                yesterday_predicted_price = previous_day1["Predictions"].round(2).to_string(index=False)
                st.markdown(f"<p style = 'text-align:center'>{yesterday_predicted_price}</p>", unsafe_allow_html=True)

            with col2:
                st.markdown("<h6 style = 'text-align:center'>Actual</h6>", unsafe_allow_html=True)

                #yesterday actual price
                yesterday_actual_price = previous_day1["Actual"].round(2).to_string(index=False)
                st.markdown(f"<p style = 'text-align:center'>{yesterday_actual_price}</p>", unsafe_allow_html=True)

            #bar graph for comparing yesterday Predicted aand actual price
            pgraph = performancegraph(yesterday_predicted_price, yesterday_actual_price)
            st.pyplot(pgraph)

            # same table can we displayed like this also
            # st.dataframe(futuredf, column_config= {"Date":st.column_config.DatetimeColumn("Date", format="YYYY-MM-DD")},use_container_width= True)

            # chat bot (optional)
            with st.container() as ChatContainer:
                with st.chat_message("Harsh") as bot:
                    bot_reply = Conclusion(yesterday_predicted_price, yesterday_actual_price)
                    st.write(bot_reply)

# About section
if selected_comp != " ":
    with tab4:
        AboutSection()

#Welcome page / message  (page 1)
if selected_comp == " ":
    WelcomeNote()
