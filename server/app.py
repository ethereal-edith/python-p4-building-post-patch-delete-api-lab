#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'

@app.route('/bakeries')
def bakeries():
    bakeries = [bakery.to_dict() for bakery in Bakery.query.all()]
    return make_response(  bakeries,   200  )

@app.route('/bakeries/<int:id>')
def bakery_by_id(id):

    bakery = Bakery.query.filter_by(id=id).first()
    bakery_serialized = bakery.to_dict()
    return make_response ( bakery_serialized, 200  )
@app.route('/baked_goods', methods=['POST']) 
def create_baked_good():
   
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()
    
    try:
        new_baked_good = BakedGood(
            name=data['name'],
            price=int(data['price']),  
            bakery_id=int(data['bakery_id'])  
        )
        db.session.add(new_baked_good)
        db.session.commit()
        return make_response(new_baked_good.to_dict(), 201)  
    except KeyError as e:
        return make_response({'error': f'Missing required field: {str(e)}'}, 400)
    except Exception as e:
        db.session.rollback()
        return make_response({'error': str(e)}, 400)

@app.route('/baked_goods/by_price')
def baked_goods_by_price():
    baked_goods_by_price = BakedGood.query.order_by(BakedGood.price.desc()).all()
    baked_goods_by_price_serialized = [
        bg.to_dict() for bg in baked_goods_by_price
    ]
    return make_response( baked_goods_by_price_serialized, 200  )
   

@app.route('/baked_goods/most_expensive')
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).limit(1).first()
    most_expensive_serialized = most_expensive.to_dict()
    return make_response( most_expensive_serialized,   200  )

@app.route('/bakeries/<int:id>', methods=['PATCH'])
def update_bakery(id):
    bakery = Bakery.query.filter_by(id=id).first()
    
    if not bakery:
        return make_response({'error': 'Bakery not found'}, 404)
    
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()
    
    try:
        if 'name' in data:
            bakery.name = data['name']
        if 'location' in data:
            bakery.location = data['location']
        
        db.session.commit()
        return make_response(bakery.to_dict(), 200)
    except Exception as e:
        db.session.rollback()
        return make_response({'error': str(e)}, 400)

@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    baked_good = BakedGood.query.filter_by(id=id).first()
    
    if not baked_good:
        return make_response({'error': 'Baked good not found'}, 404)
    
    try:
        db.session.delete(baked_good)
        db.session.commit()
        return make_response({'message': 'Baked good deleted successfully'}, 200)
    except Exception as e:
        db.session.rollback()
        return make_response({'error': str(e)}, 400)

if __name__ == '__main__':
    app.run(port=5555, debug=True)