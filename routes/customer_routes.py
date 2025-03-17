from flask import jsonify, render_template, request
from flask_login import current_user, login_required

from models import Address


def customer_routes(app, db):
    @app.route('/user/profile')
    @login_required
    def customer():
        return render_template('user/profile.html', user=current_user)

    @app.route("/address/new", methods=["POST"])
    @login_required
    def add_address():
        data = request.get_json()
        new_address = Address(
            address_line=data.get("address_line"),
            city=data.get("city"),
            state=data.get("state"),
            zip_code=data.get("zip_code"),
            customer_id=current_user.id
        )
        db.session.add(new_address)
        db.session.commit()
        return jsonify({"message": "Address added successfully!"}), 201
    

    @app.route("/address/<int:address_id>/set-preferred", methods=["POST"])
    @login_required
    def set_preferred_address(address_id):
        # Fetch the selected address
        address = Address.query.filter_by(id=address_id, customer_id=current_user.id).first()
        
        if not address:
            return jsonify({"error": "Address not found"}), 404

        # Set all addresses to "not preferred"
        Address.query.filter_by(customer_id=current_user.id).update({"is_preferred": False})

        # Set the selected address as preferred
        address.is_preferred = True
        db.session.commit()

        return jsonify({"message": "Default address updated!"}), 200
    
    @app.route("/address/<int:address_id>", methods=["DELETE"])
    @login_required
    def delete_address(address_id):
        # Fetch the address
        address = Address.query.filter_by(id=address_id, customer_id=current_user.id).first()

        if not address:
            return jsonify({"error": "Address not found"}), 404

        # Delete the address from the database
        db.session.delete(address)
        db.session.commit()

        return jsonify({"message": "Address deleted successfully!"}), 200


    # @app.route("/address/<int:address_id>", methods=["PUT"])
    # @login_required
    # def edit_address(address_id):
    #     data = request.get_json()
    #     address = Address.query.filter_by(id=address_id, customer_id=current_user.id).first()
        
    #     if not address:
    #         return jsonify({"error": "Address not found"}), 404

    #     # Update only if values are provided and not empty
    #     if data.get("address_line"):
    #         address.address_line = data["address_line"]
    #     if data.get("city"):
    #         address.city = data["city"]
    #     if data.get("state"):
    #         address.state = data["state"]
    #     if data.get("zip_code"):
    #         address.zip_code = data["zip_code"]

    #     db.session.commit()
        
    #     return jsonify({
    #         "message": "Address updated successfully!",
    #         "address": {
    #             "address_line": address.address_line,
    #             "city": address.city,
    #             "state": address.state,
    #             "zip_code": address.zip_code
    #         }
    #     }), 200


