from flask import Flask, render_template, request, jsonify
import db_utils
from topsis import TopsisAnalyzer

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    ranking = None
    error = None
    
    # Load metadata for dropdowns
    districts = db_utils.fetch_districts()
    
    default_weights = {
        'price': 0.2, 
        'area': 0.1, 
        'frontage': 0.1, 
        'foot_traffic': 0.3, 
        'employee_cost': 0.1, 
        'utilities_cost': 0.1, 
        'min_opponent_dist': 0.1 
    }
    
    current_weights = default_weights.copy()
    
    # Filters
    investment_amount = ''
    selected_district = ''
    selected_ward = ''

    if request.method == 'POST':
        try:
            # 1. Get Weights
            total_weight = 0
            for key in current_weights:
                val = float(request.form.get(key, 0))
                current_weights[key] = val
                total_weight += val
            
            if total_weight > 0:
                normalized_weights = {k: v/total_weight for k, v in current_weights.items()}
            else:
                normalized_weights = default_weights

            # 2. Get Filters
            investment_amount = request.form.get('investment_amount', '')
            selected_district = request.form.get('district', '')
            selected_ward = request.form.get('ward', '')
            
            max_price = float(investment_amount) if investment_amount else None
            
            # 3. Fetch Data with Filters
            df = db_utils.fetch_location_data(
                max_price=max_price,
                district_id=selected_district,
                ward_id=selected_ward
            )
            
            if df is not None and not df.empty:
                # 4. Run TOPSIS
                analyzer = TopsisAnalyzer(df, weights=normalized_weights)
                ranking_df = analyzer.get_ranking()
                
                ranking = ranking_df.to_dict(orient='records')
                for row in ranking:
                    row['topsis_score'] = round(row['topsis_score'], 4)
            else:
                if df is not None and df.empty:
                    error = "Không tìm thấy cửa hàng nào phù hợp với bộ lọc."
                else:
                    error = "Lỗi kết nối cơ sở dữ liệu."
                
        except Exception as e:
            error = f"Có lỗi xảy ra: {str(e)}"
    
    # Reload wards if district is selected to keep dropdown state
    wards = []
    if selected_district:
        wards = db_utils.fetch_wards(district_id=selected_district)

    return render_template('index.html', 
                           ranking=ranking, 
                           weights=current_weights, 
                           error=error,
                           districts=districts,
                           wards=wards,
                           investment_amount=investment_amount,
                           selected_district=int(selected_district) if selected_district else '',
                           selected_ward=int(selected_ward) if selected_ward else '')

@app.route('/api/wards/<int:district_id>')
def get_wards(district_id):
    wards = db_utils.fetch_wards(district_id)
    return jsonify(wards)

if __name__ == '__main__':
    app.run(debug=True)
