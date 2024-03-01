import random
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import yfinance as yf
from forex_python.converter import  CurrencyRates

def companyticker(country=None, all_comp=False):
    if country == "Indian Companies" and all_comp == False:
        indian_comp = pd.read_excel("tickerinfo.xlsx", sheet_name="indian", header=0)
        indian_comp.drop_duplicates(subset = ["name" , "ticker"] , inplace = True)
        indian_comp.reset_index(drop = True)
        return indian_comp

    elif country == "Foreign Companies" and all_comp == False:
        foreign_comp = pd.read_excel("tickerinfo.xlsx", sheet_name="international", header=0)
        foreign_comp.drop_duplicates(subset= ["name", "ticker"], inplace = True)
        foreign_comp.reset_index(drop=True)

        # indian_rupees = 83.43
        # foreign_comp["Close"] = foreign_comp["Close"] * indian_rupees
        return foreign_comp

    else:
        indian_comp = pd.read_excel("tickerinfo.xlsx", sheet_name="indian", header=0).sort_values(
            by="name").reset_index(drop=True)
        foreign_comp = pd.read_excel("tickerinfo.xlsx", sheet_name="international", header=0).sort_values(
            by="name").reset_index(drop=True)
        all_companies = pd.concat([indian_comp, foreign_comp], axis=0, ignore_index=True)
        all_companies.drop_duplicates(subset= ["name", "ticker"], inplace = True)

        return all_companies


class DataLoad:
    def load_data(self, tickertbl, company,  startdate=None, enddate=None):
        self.selected_comp_ticker = tickertbl[tickertbl["name"] == company]["ticker"].to_string(index=False)
        try:
            stockdata = yf.download(self.selected_comp_ticker, start="2018-01-01")
            stockdata.reset_index(inplace = True) #reset the index to (0 to n), as the default index is datecolumn

            stockdata= stockdata[stockdata["Date"].dt.date < pd.to_datetime("today").date()]  #only fetch data upto the previous date. i.e, dont fetch the today's (current) data.

        except :
            print("Data for this company is not available.")

        else:
            if startdate is None and enddate is None:
                return stockdata

            else:
                selected_dates = stockdata[(stockdata["Date"]  >= startdate) & (stockdata["Date"] <= enddate)]

                return selected_dates

    def todaysinfo(self):
        TodayInfo = yf.Ticker(self.selected_comp_ticker)
        try:
            TodayOpen = TodayInfo.info['open']

        except:
            TodayOpen = "Not Available"

        try:
            RecentPrice =   TodayInfo.info['currentPrice']


        except:
            RecentPrice =  "Not Available"

        try :
            TodayHigh = TodayInfo["dayhigh"]

        except :
            TodayHigh = "Not Available"

        return RecentPrice , TodayOpen , TodayHigh

    def currencyrate(self,convert_to = "USD"):
        original_curr = yf.Ticker(self.selected_comp_ticker).info["currency"]
        try:
            curr_rate = CurrencyRates().get_rate(original_curr , convert_to )
        except:
            curr_rate = 0.012
        return  curr_rate

def trend(data, column, startdate=None, enddate=None):
    filterdf = data[(data["Date"] >= startdate) & (data['Date'] <= enddate)]
    graph1 = plt.figure(figsize=(15, 7))
    plt.plot(filterdf["Date"], filterdf[column])
    plt.xlabel("Date")
    plt.ylabel("Closing Price")

    return graph1


def predictedtrend(past_df, startdate=None, enddate=None):

    past_df_filtered = past_df[(past_df["Date"] >= startdate) & (past_df['Date'] <= enddate)]
    past_df_filtered["Actual"] = past_df_filtered["Actual"]

    graph2 = plt.figure(figsize=(15, 7))
    plt.plot(past_df_filtered["Date"], past_df_filtered["Actual"], color="orange", label="Actual")
    plt.plot(past_df_filtered["Date"], past_df_filtered["Predictions"], color="green", label="Predicted")
    plt.legend()
    plt.xlabel("Dates")
    plt.ylabel("Closing Price")

    return graph2


def futuretrend(futuredf, currentdf, column="Close"):
    graph3 = plt.figure(figsize=(15, 5))
    plt.plot(currentdf["Date"][-150:], currentdf[column][-150:], label="Past Values")
    plt.plot(futuredf["Date"], futuredf["Predictions"], color="green", label="Future Values")
    plt.legend(loc="upper left")
    plt.xlabel("Dates")
    plt.ylabel("Closing Price")
    return graph3


def pastbargraph(past_df, column="Close", startdate=None, enddate=None):

    past_df_filtered = past_df[(past_df["Date"] >= startdate) & (past_df['Date'] <= enddate)]
    past_df_filtered["Date"] = past_df_filtered["Date"].dt.date

    if startdate is not None and enddate is not None:
        fig = plt.figure(figsize=(15, 5))
        # plt.setp(plt.gca().patches, 'width', 0.6)
        sns.set_style("darkgrid")

        sns.barplot(data = past_df_filtered,x="Date", y="Actual", color="red", width=0.25)
        sns.barplot(data = past_df_filtered, x="Date", y="Predictions", color="lightgreen", width=0.25)

        plt.xlabel("Dates")
        plt.ylabel("Closing Price")

        if len(past_df_filtered) > 10:
            plt.xticks([])
        return fig


def displaydisclaimer():
    disclaimer_head = "<h4 style = 'text-align : center'>Disclaimer on Stock Prediction.</h4>"
    st.markdown(disclaimer_head, unsafe_allow_html=True)

    st.markdown('<br>', unsafe_allow_html=True)

    sub_head1 = "<h6>Important Notice: Risk Disclaimer for Stock Predictions</h6>"
    st.markdown(sub_head1, unsafe_allow_html=True)
    st.markdown('''
                We appreciate your interest in our stock prediction model deployed through Streamlit. 
                However, it is crucial to emphasize that the predictions generated by the model are based on historical data and various assumptions.
                Stock markets inherently involve uncertainties and carry financial risks.
                ''', unsafe_allow_html=True)

    sub_head2 = "<h6>Disclaimer:</h6>"
    st.markdown(sub_head2, unsafe_allow_html=True)
    st.markdown('''
        The stock predictions provided by our Artificial Neural Network (ANN) model and displayed through Streamlit are for informational purposes only. 
        They should not be considered as financial advice. The volatile nature of financial markets carries inherent risks, and past performance does not guarantee future results.
            ''', unsafe_allow_html=True)

    sub_head3 = "<h6>User Caution Advised:</h6>"
    st.markdown(sub_head3, unsafe_allow_html=True)
    st.markdown('''
        Investing in stocks involves uncertainties, and decisions based solely on automated predictions may lead to financial losses.
         The market is dynamic, influenced by various factors, and unforeseen events can impact asset values.
         ''', unsafe_allow_html=True)

    sub_head4 = "<h6>Exercise Caution:</h6>"
    st.markdown(sub_head4, unsafe_allow_html=True)
    st.markdown('''
            We strongly recommend users to conduct thorough research, consult with financial professionals,
            and consider their risk tolerance before making any investment decisions. Our model is a tool to aid in decision-making, 
            but it is not a substitute for careful analysis and judgment.
            ''', unsafe_allow_html=True)

    sub_head5 = "<h6>No Guarantees:</h6>"
    st.markdown(sub_head5, unsafe_allow_html=True)
    st.markdown('''
            There are no guarantees or assurances regarding the accuracy or reliability of the predictions. Market conditions can change rapidly, 
            and the model may not account for all factors influencing stock prices.

             ''', unsafe_allow_html=True)

    sub_head6 = "<h6>Final Note:</h6>"
    st.markdown(sub_head6, unsafe_allow_html=True)
    st.markdown('''
               While we strive to provide valuable insights, it is essential to exercise caution and diligence when using stock predictions. Remember that all investments carry risks,
               and you should diversify your portfolio to mitigate potential losses.
                ''', unsafe_allow_html=True)


def conclusion(predicted, actual):
    difference = float(actual) - float(predicted)

    if difference == 0:
        messages = ["WOW!! What a perfect prediction it is.", "Its a Perfect One."]
        return random.choice(messages)
    elif difference <= 1:
        messages = ["Great !!, I am soo close.", "Appreciated!!, I predicted it soo well. "]
        return random.choice(messages)
    elif difference <= 4:
        messages = ["Not Bad!!, My prediction is not soo bad. ",
                    "Ohh!!, I was close. But its still considerable isn't ?? "]
        return random.choice(messages)
    else:
        return "OOPS!!, I just missed it this time. Sorry!!"


def performancegraph(predicted, actual):
    dt = {
        "labels": ["Prediction", "Actual"],
        "Values": [float(predicted), float(actual)]
    }
    sns.set_style("darkgrid")
    fig = plt.figure(figsize=(12, 4))
    sns.barplot(data=dt, x="labels", y="Values", width=0.25)
    plt.xlabel("Predicted & Actual")
    plt.ylabel("Closing Price")
    # plt.grid(linestyle = "--")

    return fig


def aboutsection():
    st.markdown(
        """
        **Understanding Stock Prediction Models:**

        A Stock Prediction Model is a computational tool designed to analyze historical stock market data 
        and make predictions about future price movements. These models leverage various algorithms and 
        techniques from the field of machine learning to identify patterns, trends, and dependencies within 
        the data. The ultimate goal is to assist investors and traders in making informed decisions about 
        buying or selling stocks.

        **The Power of LSTM (Long Short-Term Memory):**

        LSTM, or Long Short-Term Memory, is a type of recurrent neural network (RNN) architecture specifically 
        crafted to address the challenges of learning and remembering patterns in sequential data. Traditional 
        neural networks struggle with retaining information over long sequences, but LSTM excels at capturing 
        dependencies and trends over extended periods. In the context of stock prediction, LSTM's ability to 
        factor in historical data and learn from it over time makes it a valuable tool for forecasting future 
        price movements.

        **Why Caution is Essential:**

        While the allure of predicting stock prices using advanced models is undeniable, it's crucial to exercise 
        caution and recognize the inherent financial risks associated with relying solely on such predictions. 
        Here are a few reasons why prudence is necessary:

        1. **Market Dynamics are Complex:** Stock markets are influenced by a multitude of factors, including 
        economic indicators, geopolitical events, and investor sentiment. No model can account for all these 
        variables with absolute certainty.

        2. **Past Performance is Not Indicative of Future Results:** Despite the sophistication of LSTM and other 
        predictive models, the stock market remains inherently unpredictable. Historical data provides a foundation 
        for learning, but it doesn't guarantee future outcomes.

        3. **Financial Markets are Dynamic:** The dynamics of financial markets evolve, and unforeseen events can 
        have a significant impact. A model trained on historical data may struggle to adapt to unprecedented 
        circumstances, leading to inaccurate predictions.

        4. **Overfitting and Noise:** Models, especially those with a high level of complexity, may fall victim 
        to overfitting, where they perform exceptionally well on historical data but fail to generalize effectively 
        to new data. Additionally, market data can contain noise, misleading the model and leading to erroneous 
        predictions.

        **A Personal Project's Limitations:**

        As a personal project developed by a newcomer in the field of data science, this Stock Prediction Model 
        serves as a valuable learning experience. However, it's essential to recognize its limitations:

        1. **Ongoing Learning Process:** The model is a work in progress, and continuous refinement is necessary. 
        Updates and improvements are part of the ongoing learning process.

        2. **Educational Purpose:** This project is primarily intended for educational purposes, showcasing the 
        application of LSTM in stock prediction. It's not a foolproof investment strategy.

        3. **No Substitute for Professional Advice:** Investors should not rely solely on the predictions generated 
        by this model for making financial decisions. Consulting with financial professionals and considering a 
        diversified approach to investing is crucial.

        In conclusion, while Stock Prediction Models, including those powered by LSTM, can offer valuable insights, 
        they should be regarded as tools rather than crystal balls. Combining data-driven analysis with a comprehensive 
        understanding of market dynamics and a diversified investment strategy is key to navigating the complex world 
        of finance responsibly.
        """
    )


def welcomenote():
    st.markdown(
        """
        <h2> Welcome to Your Personal Stock Prediction Hub! </h2> 📈 

        Hey there, fellow market enthusiast! 👋 Get ready to embark on an exciting journey through the dynamic world of stocks with my personally crafted Stock Prediction Model. 🌐

        <h5> What's in Store for You?</h5>
        Explore the fascinating realm of financial forecasting as we delve into the intricate patterns and trends that shape the stock market. My custom-built model is designed to analyze historical stock data, unravel complex market dynamics, and make predictions that might just give you the edge in your investment decisions.

        <br>
        <h5>How to Navigate:</h5>
        <ol>
            <li><strong>Choose Your Stock:</strong> Select the stock you're interested in, and let the magic unfold.</li>
            <li><strong>View Predictions:</strong> Dive into the predictions generated by the model and gain insights into potential future stock prices.</li>
            <li><strong>Explore Historical Trends:</strong> Take a stroll down memory lane as you examine historical data and witness the model's performance over time.</li>
            <li><strong>Stay Informed:</strong> Keep an eye on market news and updates to complement the predictions and make well-informed decisions. </li>
        </ol>
        <h5> Behind the Scenes: </h5>
        <p>This project is a labor of love, fueled by a passion for data science and a relentless pursuit of understanding the financial markets. While no model can guarantee absolute accuracy, this model strives to provide valuable insights to aid your investment journey.</p>

        ⚠️ **Disclaimer**: Don't blindly trust any model, including this one. Stock markets are inherently unpredictable, and all predictions come with a degree of uncertainty. Always perform thorough research and consider multiple factors before making investment decisions.

        <h5>Time Series Analysis:</h5>
        <p>Time series analysis involves studying data collected over time to identify patterns, trends, and seasonality. In the context of stock prediction, understanding how historical stock prices evolve over time is crucial. It helps in building models to make informed predictions based on past behavior.</p>

        <h5>Cheers to informed decisions and prosperous investments! 🥂</h5>
        
        <br>
        <p>Harsh Thakur<br>
        <b>Creator of the Stock Prediction Model</b></p>
        """
        , unsafe_allow_html=True)
