from flask import current_app as app
from flask import redirect, render_template, url_for, request, flash

from .forms import StockForm
from .charts import *


@app.route("/", methods=['GET', 'POST'])
@app.route("/stocks", methods=['GET', 'POST'])
def stocks():
    
    form = StockForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            #Get the form data to query the api
            symbol = request.form['symbol']
            chart_type = request.form['chart_type']
            time_series = request.form['time_series']
            start_date = convert_date(request.form['start_date'])
            end_date = convert_date(request.form['end_date'])

            if end_date <= start_date:
                #Generate error message as pass to the page
                err = "ERROR: End date cannot be earlier than Start date."
                chart = None
            else:
                #query the api using the form data
                err = None
                 
                #THIS IS WHERE YOU WILL CALL THE METHODS FROM THE CHARTS.PY FILE AND IMPLEMENT YOUR CODE
                do_again = True
                while do_again:
                #get user input
                    app.config['SECRET_KEY'] = 'ABCD1234'
                    inputs = get_user_input()
                    # print('\ninputs = \n', inputs)

                    #make api call
                    api_data = call_api(inputs, API_KEY)
                    # print('\napi_data = \n', api_data)

                    #filter out unwanted dates
                    filtered_api_data = filter_dates(api_data, inputs)
                    # print('\nfiltered_api_data = \n', filtered_api_data)

                    if filtered_api_data:
                  
            
                
                
                
                
                    #This chart variable is what is passed to the stock.html page to render the chart returned from the api
                        chart = render_graph(filtered_api_data, inputs)
                    #render graph in browser
                  # print("FILTERED DATA FROM INSIDE IF", filtered_api_data)
                  # print("test")
                  
                    else:
                      print("An unexpected error occurred...")
                  # render_default()
                      pass
                    go_again = input('Would you like to see more stock data? (Y/N): ')
                    go_again = go_again.upper()
                    if (go_again == 'Y'):
                        do_again = True
                    else:
                        do_again = False

            return render_template("stock.html", form=form, template="form-template", err = err, chart = chart)
    
    return render_template("stock.html", form=form, template="form-template")
