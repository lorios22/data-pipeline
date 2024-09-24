import json
import requests

# Format any nomber in shorten way
def format_number_short(number):
    try:
        formatted_number = float(number)
    except (TypeError, ValueError):
        return "Invalid input"
    if formatted_number < 0:
        formatted_number = abs(formatted_number)
        negative_flag = True
    else:
        negative_flag = False
    suffixes = ['', 'k', 'M', 'B', 'T', 'P', 'E', 'Z', 'Y']
    suffix_index = 0
    while formatted_number >= 1000 and suffix_index < len(suffixes)-1:
        formatted_number /= 1000.0
        suffix_index += 1
    formatted_string = '{:.3f}{}'.format(formatted_number, suffixes[suffix_index])
    if negative_flag:
        formatted_string = '-' + formatted_string
    return formatted_string

# Get basic data for all the available protocols on Defillama
def get_llama_protocols():
    url = 'https://api.llama.fi/protocols'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            protocols_data = []
            for protocol in data:
                protocols_data.append({
                    'id': protocol['id'],
                    'name': protocol['name'],
                    'slug': protocol['slug'],
                    'tvl': protocol['tvl'],
                    'change_1d': protocol['change_1d'],
                    'change_7d': protocol['change_7d'],
                    'chains': protocol['chains']
                })
            # Writes the response to a JSON file
            with open("llama_protocols.json", "w") as json_file:
                json.dump(protocols_data, json_file, indent=4)
            print("All protocols from Defillama saved successfully.")
            return {'message': protocols_data, 'success': True}
        else:
            return {'message': response.content, 'success': False}
    except Exception as e:
        return {'message': str(e), 'success': False}
    
# Get the TVL of a protocol
def get_protocol_tvl(token_id):
    formatted_id = str(token_id).casefold()
    url = f"https://api.llama.fi/tvl/{formatted_id}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return {'tvl': data, 'success': True}
        else:
            return {'message': response.content.decode('utf-8'), 'success': False}
    except Exception as e:
        return {'message': f"An error occurred: {str(e)}", 'success': False}
    
# Get fees and revenue of all available protocols in Defilllama
def get_fees_revenue_all_protocols(token_name):
    url = f"https://api.llama.fi/overview/fees/{token_name}?excludeTotalDataChart=true&excludeTotalDataChartBreakdown=true&dataType=dailyFees"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            protocols_data = {}
            protocols_data['chain'] = data.get('chain', None)
            protocols_data['dailyRevenue'] = data.get('dailyRevenue', None)
            protocols_data['dailyUserFees'] = data.get('dailyUserFees', None)
            protocols_data['dailyHoldersRevenue'] = data.get('dailyHoldersRevenue', None)
            protocols_data['dailyProtocolRevenue'] = data.get('dailyProtocolRevenue', None)
            # # Writes the response to a JSON file
            # with open("llama_protocols_details.json", "w") as json_file:
            #     json.dump(protocols_data, json_file, indent=4)
            # print("All protocols from Defillama saved successfully.")
            return {'message': protocols_data, 'success': True}
        else:
            return {'message': response.content, 'success': False}
    except Exception as e:
        return {'message': str(e), 'success': False}
    
# function to provide a default value for sorting
def get_token_symbol(item):
    token_symbol = item.get('tokenSymbol')
    return token_symbol if token_symbol is not None else ''

result= get_protocol_tvl(4270)
print(result)
#get_fees_revenue_all_protocols()