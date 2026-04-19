from flask import Flask
from controllers.visitor_controller import visitor_bp
from db import init_db, db
from models.website_visitor import WebsiteVisitor
import json

def clear_and_test():
    app = Flask(__name__)
    init_db(app)
    app.register_blueprint(visitor_bp, url_prefix='/api')
    
    with app.app_context():
        print("Clearing website_visitors table for fresh testing...")
        db.session.query(WebsiteVisitor).delete()
        db.session.commit()
        print("Table cleared!")

        with app.test_client() as client:
            print("\n--- Test 1: Standard request ---")
            res = client.get('/api/public/visitor-count')
            print(json.loads(res.data))

            print("\n--- Test 2: Request with X-Forwarded-For ---")
            res = client.get('/api/public/visitor-count', headers={'X-Forwarded-For': '8.8.8.8'})
            print(json.loads(res.data))

            print("\n--- Test 3: Request with CF-Connecting-IP (Cloudflare) ---")
            res = client.get('/api/public/visitor-count', headers={'CF-Connecting-IP': '1.1.1.1'})
            print(json.loads(res.data))
            
            # Check final count
            count = db.session.query(WebsiteVisitor.ip_address).distinct().count()
            print(f"\nFinal Unique Visitor Count in DB: {count}")
            if count == 3:
                print("\nVerification SUCCESSFUL: Multiple IPs correctly identified!")
            else:
                print(f"\nVerification FAILED: Expected 3 unique IPs, found {count}")

if __name__ == "__main__":
    clear_and_test()
