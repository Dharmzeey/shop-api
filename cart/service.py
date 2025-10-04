from django.conf import settings

from products.serializers import ProductSerializer
from products.models import Product
from base.models import LGA


class Cart:
    def __init__(self, request):
        """
        initialize the cart and also the address
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        address = self.session.get(settings.ADDRESS_SESSION_ID)
        if not cart:
            # save an empty cart in session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        if not address:
            address = self.session[settings.ADDRESS_SESSION_ID] = {}
        self.address = address

    def save(self):
        self.session.modified = True
        

    def increament(self, product_uuid):
        product = Product.objects.get(uuid=product_uuid)
        if  (product_uuid in self.cart) and (product.stock > self.cart[product_uuid]["quantity"]):
            self.cart[product_uuid]["quantity"] += 1
            self.save()
            return True
        return False

            
    def decreament(self, product_uuid):
        if (product_uuid in self.cart) and (self.cart[product_uuid]["quantity"] > 1):
            self.cart[product_uuid]["quantity"] -= 1
            self.save()
            return True
        return False
            
    def update(self, product_uuid, quantity):
        product = Product.objects.get(uuid=product_uuid)
        if  (product_uuid in self.cart) and (product.stock > int(quantity) + self.cart[product_uuid]["quantity"]):
            self.cart[product_uuid]["quantity"] += int(quantity)
            self.save()
            return True
        elif product_uuid in self.cart:
            self.cart[product_uuid]["quantity"] = product.stock
            self.save()
            return True
        elif  (product_uuid not in self.cart) and product.stock > int(quantity):
            product = Product.objects.get(uuid=product_uuid)
            self.cart[product_uuid] = {
                "quantity": int(quantity),
                "price":  product.price# just for initialization will be updated later in the __iter__()
            }
            self.save()
            return True
        return False

    def remove(self, product_uuid):
        if product_uuid in self.cart:
            del self.cart[product_uuid]
            self.save()
            return True
        return False

    def __iter__(self, request):
        """
        Loop through cart items and fetch the products from the database
        """
        product_uuids = self.cart.keys()
        products = Product.objects.filter(uuid__in=product_uuids)
        cart = self.cart.copy()
        for product in products:
            cart_item = cart[str(product.uuid)]
            cart_item["product"] = ProductSerializer(product, context={'request': request}).data
            cart_item["price"] = product.price #add the price k,v to the dict
            cart_item["total_price"] = product.price * cart_item["quantity"] #add the total_price k,v to the dict

            self.cart[str(product.uuid)]["price"] = product.price #updates the price per product in the cart field of this class instance
            yield cart_item

    def __len__(self):
        """
        Count all items in the cart
        """
        return sum(item["quantity"] for item in self.cart.values())

    def get_total_price(self):
        return sum(item["price"] * item["quantity"] for item in self.cart.values())

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()
        
    
    def include_address(self, use_default, serializer=None, user_phone=None, user_info=None, user_address=None):
        if use_default:           
             address_data = {
                "name" : f"{user_info.first_name} {user_info.last_name}",
                "phone_number" : user_phone,
                "state" : user_address.state.id,
                "city_town" : user_address.city_town,
                "lga" : user_address.lga.id,
                "prominent_motor_park" : user_address.prominent_motor_park,
                "landmark_signatory_place" : user_address.landmark_signatory_place,
                "address" : user_address.address,
            }
            # Delivery Fee 
             delivery_fee=  user_address.lga.delivery_fee
        else:
            lga = LGA.objects.get(id=serializer["lga"])
            address_data = {
                "name" : serializer["name"],
                "phone_number" : serializer["phone_number"],
                "state" : serializer["state"],
                "city_town" : serializer["city_town"],
                "lga" : serializer["lga"],
                "prominent_motor_park" : serializer.get("prominent_motor_park", None),
                "landmark_signatory_place" : serializer.get("landmark_signatory_place", None),
                "address" : serializer["address"],
            }           
            # Delivery Fee
            delivery_fee = lga.delivery_fee
        self.address['address_info'] = address_data
        self.address['delivery_fee'] = delivery_fee
        self.save()
        return address_data
