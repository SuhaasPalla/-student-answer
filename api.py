from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Firebase initialization function
def initialize_firebase():
    """
    Initialize Firebase with properly formatted service account credentials.
    """
    # Service account info
    service_account_info = {
      "type": "service_account",
      "project_id": "transgrade-5244b",
      "private_key_id": "fadfb9719e9a05c2c89859ac3c4a4edbedbbac6d",
      "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDH7bhSjbFgGFCP\nZap6xCQg69PMOpejVTENSvwaP5lmgbDwGg4dJ4NBL20Ft8gTaYK8jY5Qqne7qXg1\nucyCdkIyd0Lha8dtJpaZ+fi1TQj7WfZbv4eiKlfnj64fgB8StOc2UZaPjPbTdXO2\n7O6n9LsjVmREpX+a9aaeeKbNsUPqCKwYZS08+Go1aLk5+7JByzf9Avbe1hPBg1CX\n1TBThY2nPOnDfU0tXzVJaGZO34nhS4Bkc2wa6jD7/ewMUKnLfa6QvwLkmQxGN3Ko\nJkKwSRciKkTCvEdWyUU0z76kHUeGiihLeicZPu/bDQ10FFudwHim5Y6+TQsvHqBX\nxN8taBg5AgMBAAECggEAE1QoPdL1ExVGtJZfpP7Rf11NXLFNd70EwQQ+20rKyd4/\n/PaH5smrJuIu6B6ceUP6H8CPwby5VqtLs+YCn5pPTBG7pY+F+EeCx+Ai62RHOgW4\ni6Y4trThSsHZU7JPTr+umtHIfJhkRI1WYpkFebdvYDs59mkJrTGSqj9/4OMCbd28\n4RoSobbBkWydy2FOVK8LVoE4JqT+lNiXcUY5QP+OMXVSjt2Z1wfAAeDrJ7V011oF\nSNLKAF5VpGoHxaqtGS2NqGDth4OxQ9F60zfRWDNaK2t9RO2SeJtu6flSqW1v9ObG\nYW9VxuG0Rw/3Y96AXM95hArg1CDJyz6DQ6TL4TfLAQKBgQD1o/YIsCH34ArJ3MqZ\nagRStHu5QgMaudKGyrnovu57u3Em5/SoYDwdNktPi7roN78FXdqKvZFxQW2QAIu4\nAHSHDTjKDgQZUeATAX/1ar00TRu+zACVl4AQa+Lo65HoBrWXGZoETLCmLbqBwF+X\ncIfWTV0LldC1dOv2MxRFqupoewKBgQDQXDvr1NzHVhY1gW4ea0blDyHMz10a5SNc\ny+huE5Z0ygmo1GqN/OlGOygy268dRBmLuAx7vfrEyhef799WfGIXHMsnsGQcBlTX\ntB5cI72RbWTMaV2ocnD7rXDZfRDP48KoIsah5sIzV9FQt/5K1KmCh+azCWPaabNf\nEPhgYLn12wKBgFwCQlIWx2J1hRT/otO8JkpkWEOYOll0aSscHG7VtbabC1MrZzT6\ndwnqIGN3T1dUKjT0Zru5LhViEIvz6GHPqdY8WZ01isuBI5F66lce2CgTCeV5vG5M\nBSghgSkFs+1ZNgOXD1207CYS0t1vFV9AQ2E+MS/5ued+GDRsBZfi4VKpAoGAUJDp\nhpYHTHioG8ZRSyfWAOop+qTP7n9dfhtGY5HlYoFg3MxN61s45DQppgi2HI3hhtoC\n0bIzDfbKzcgVxr5Pu3ohv9X/z6pPEh0OhDg5q8rt5/ByC5k8wMRe12n5nzkFYrgX\nsDCnNO0m/Zw3kr3KUbO069Ocra6jcgYA1FtybHMCgYAl2s6Q9XzibPu+VjQ7s0ko\ntE6WyhT755964PiEkdyAB8sOBIn2haWF/rfhRmJcol+gHEBT6C+zgr0lYFbAONs2\nCUQo5S9jJmJEuAaCzPfhtzO2jDtraJUcsffojOdP0RowSdYfqG6yjXlVq7IgnIbp\nZvXgrFLWJRjn2E4RwbBAvA==\n-----END PRIVATE KEY-----\n",
      "client_email": "firebase-adminsdk-fbsvc@transgrade-5244b.iam.gserviceaccount.com",
      "client_id": "110456888702790733842",
      "auth_uri": "https://accounts.google.com/o/oauth2/auth",
      "token_uri": "https://oauth2.googleapis.com/token",
      "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
      "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40transgrade-5244b.iam.gserviceaccount.com",
      "universe_domain": "googleapis.com"
    }
    
    # Save credentials to a properly formatted JSON file
    service_account_path = "firebase_credentials.json"
    
    with open(service_account_path, "w") as f:
        json.dump(service_account_info, f)
    
    try:
        # Initialize Firebase with the credentials file
        cred = credentials.Certificate(service_account_path)
        if not firebase_admin._apps:  # Only initialize if not already initialized
            firebase_admin.initialize_app(cred)
        print("✅ Firebase initialized successfully")
        
        # Clean up the credentials file
        if os.path.exists(service_account_path):
            os.remove(service_account_path)
            
        return firestore.client()
    except Exception as e:
        print(f"❌ Error initializing Firebase: {e}")
        
        # Clean up the credentials file
        if os.path.exists(service_account_path):
            os.remove(service_account_path)
            
        return None

# Helper function to convert Firestore timestamp to readable format
def format_timestamp(timestamp):
    """Convert Firestore timestamp to readable string"""
    if timestamp:
        try:
            return timestamp.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return str(timestamp)
    return None

@app.route('/api/student/<student_id>', methods=['GET'])
def get_student_data(student_id):
    """
    Get all data for a specific student by ID
    
    Usage: GET /api/student/student_abc123
    """
    try:
        db = initialize_firebase()
        if not db:
            return jsonify({
                'error': 'Firebase initialization failed',
                'success': False
            }), 500
        
        doc_ref = db.collection('student_answers').document(student_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({
                'error': f'Student with ID "{student_id}" not found',
                'success': False
            }), 404
        
        data = doc.to_dict()
        
        # Format timestamp for readability
        if 'timestamp' in data:
            data['timestamp'] = format_timestamp(data['timestamp'])
        
        return jsonify({
            'success': True,
            'student_id': student_id,
            'data': data
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Error retrieving student data: {str(e)}',
            'success': False
        }), 500

@app.route('/api/student/<student_id>/ocr', methods=['GET'])
def get_student_ocr(student_id):
    """
    Get only OCR data for a specific student
    
    Usage: GET /api/student/student_abc123/ocr
    """
    try:
        db = initialize_firebase()
        if not db:
            return jsonify({
                'error': 'Firebase initialization failed',
                'success': False
            }), 500
        
        doc_ref = db.collection('student_answers').document(student_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({
                'error': f'Student with ID "{student_id}" not found',
                'success': False
            }), 404
        
        data = doc.to_dict()
        ocr_data = data.get('ocr', None)
        
        if not ocr_data:
            return jsonify({
                'error': f'No OCR data found for student "{student_id}"',
                'success': False
            }), 404
        
        return jsonify({
            'success': True,
            'student_id': student_id,
            'ocr': ocr_data,
            'timestamp': format_timestamp(data.get('timestamp')),
            'context': data.get('context', 'Unknown')
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Error retrieving OCR data: {str(e)}',
            'success': False
        }), 500

@app.route('/api/student/<student_id>/restructured', methods=['GET'])
def get_student_restructured(student_id):
    """
    Get only restructured data for a specific student
    
    Usage: GET /api/student/student_abc123/restructured
    """
    try:
        db = initialize_firebase()
        if not db:
            return jsonify({
                'error': 'Firebase initialization failed',
                'success': False
            }), 500
        
        doc_ref = db.collection('student_answers').document(student_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({
                'error': f'Student with ID "{student_id}" not found',
                'success': False
            }), 404
        
        data = doc.to_dict()
        restructured_data = data.get('restructured_json', None)
        
        if not restructured_data:
            return jsonify({
                'error': f'No restructured data found for student "{student_id}"',
                'success': False
            }), 404
        
        return jsonify({
            'success': True,
            'student_id': student_id,
            'restructured_json': restructured_data,
            'timestamp': format_timestamp(data.get('timestamp')),
            'context': data.get('context', 'Unknown')
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Error retrieving restructured data: {str(e)}',
            'success': False
        }), 500

@app.route('/api/students', methods=['GET'])
def get_all_students():
    """
    Get list of all students with basic info
    
    Usage: GET /api/students
    Optional query parameters:
    - limit: Maximum number of results (default: 50)
    - context: Filter by context (e.g., "PDF Upload", "Image Upload")
    """
    try:
        db = initialize_firebase()
        if not db:
            return jsonify({
                'error': 'Firebase initialization failed',
                'success': False
            }), 500
        
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        context_filter = request.args.get('context', None)
        
        # Build query
        query = db.collection('student_answers')
        
        if context_filter:
            query = query.where('context', '==', context_filter)
        
        # Limit results
        query = query.limit(limit)
        
        docs = query.stream()
        students = []
        
        for doc in docs:
            data = doc.to_dict()
            student_info = {
                'student_id': doc.id,
                'context': data.get('context', 'Unknown'),
                'timestamp': format_timestamp(data.get('timestamp')),
                'has_ocr': 'ocr' in data and data['ocr'] is not None,
                'has_restructured': 'restructured_json' in data and data['restructured_json'] is not None
            }
            students.append(student_info)
        
        return jsonify({
            'success': True,
            'count': len(students),
            'students': students
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Error retrieving students list: {str(e)}',
            'success': False
        }), 500

@app.route('/api/students/search', methods=['GET'])
def search_students():
    """
    Search students by various criteria
    
    Usage: GET /api/students/search?context=PDF Upload&has_ocr=true
    Query parameters:
    - context: Filter by context
    - has_ocr: Filter students with/without OCR data (true/false)
    - has_restructured: Filter students with/without restructured data (true/false)
    - limit: Maximum number of results (default: 50)
    """
    try:
        db = initialize_firebase()
        if not db:
            return jsonify({
                'error': 'Firebase initialization failed',
                'success': False
            }), 500
        
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        context_filter = request.args.get('context', None)
        has_ocr = request.args.get('has_ocr', None)
        has_restructured = request.args.get('has_restructured', None)
        
        # Build query
        query = db.collection('student_answers')
        
        if context_filter:
            query = query.where('context', '==', context_filter)
        
        # Limit results
        query = query.limit(limit)
        
        docs = query.stream()
        students = []
        
        for doc in docs:
            data = doc.to_dict()
            
            # Apply client-side filtering for has_ocr and has_restructured
            has_ocr_data = 'ocr' in data and data['ocr'] is not None
            has_restructured_data = 'restructured_json' in data and data['restructured_json'] is not None
            
            # Filter based on has_ocr parameter
            if has_ocr is not None:
                if has_ocr.lower() == 'true' and not has_ocr_data:
                    continue
                if has_ocr.lower() == 'false' and has_ocr_data:
                    continue
            
            # Filter based on has_restructured parameter
            if has_restructured is not None:
                if has_restructured.lower() == 'true' and not has_restructured_data:
                    continue
                if has_restructured.lower() == 'false' and has_restructured_data:
                    continue
            
            student_info = {
                'student_id': doc.id,
                'context': data.get('context', 'Unknown'),
                'timestamp': format_timestamp(data.get('timestamp')),
                'has_ocr': has_ocr_data,
                'has_restructured': has_restructured_data
            }
            students.append(student_info)
        
        return jsonify({
            'success': True,
            'count': len(students),
            'students': students,
            'filters_applied': {
                'context': context_filter,
                'has_ocr': has_ocr,
                'has_restructured': has_restructured,
                'limit': limit
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Error searching students: {str(e)}',
            'success': False
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    try:
        db = initialize_firebase()
        firebase_status = "connected" if db else "failed"
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'firebase': firebase_status,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }), 500

if __name__ == '__main__':
    print("🚀 Starting Firebase Data API...")
    print("📊 Available endpoints:")
    print("   GET /api/health - Health check")
    print("   GET /api/students - List all students")
    print("   GET /api/students/search - Search students with filters")
    print("   GET /api/student/<id> - Get complete student data")
    print("   GET /api/student/<id>/ocr - Get student OCR data only")
    print("   GET /api/student/<id>/restructured - Get student restructured data only")
    print()
    app.run(debug=True, port=5001)