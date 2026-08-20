# default_correlation_id = "streaming_0"
# default_mode = 1 #1 LTP,  2 QUOTE, 3 SNAP_QUOTE
# default_token_list = [
#     {
#         "exchangeType": 1,      # NSE Cash
#         "tokens": ["14366"]
#     }
# ]

default_correlation_id = "streaming_mcx"
default_mode = 1 #1 LTP,  2 QUOTE, 3 SNAP_QUOTE
default_token_list = [
    {
        "exchangeType": 5,      #1 NSE_CM, 2 NSE_FO, 3 BSE_CM, 4 BSE_FO, MCX_FO 
        "tokens": ["562056"]    
    }
]
# account settings
default_initial_balance = 100000.0 # 1 lac
default_daily_loss_limit = 5000.0 # 5k







