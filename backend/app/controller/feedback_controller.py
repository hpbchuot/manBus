from flask import request, Blueprint
from app.main import api
from app.main.service.feedback_service import add, get_all_feed, generate_pdf_report
from app.main.utils.dto import Feedback

# api = Feedback.api
# _fb = Feedback._fb
# fb = Feedback.pagination
# date_range_model = Feedback.date_range_model
feedback_api = Blueprint('feedback_api', __name__)

# @api.route('/add')
# class AddFeedBack(Resource):
#     @api.doc('send fb')
#     @api.expect(_fb, validate=True)
#     def post(self):
#         """List all registered users"""
#         token= request.headers.get('Authorization')
#         post_data = request.json
#         return add(post_data,token)
@feedback_api.route('/get-all-feed',methods=['GET'])
def FeedbackList():
    page = request.args.get('page', 1, type=int)
    pageSize = request.args.get('page_size', 10, type=int)
    return get_all_feed(page, pageSize)
# @api.route('/generate')
# class GeneratePdfReport(Resource):
#     @api.doc('Tạo báo cáo feedback dạng PDF')
#     @api.expect(date_range_model, validate=True)
#     def post(self):
#         data = request.json
#         print(data)
#         """Tạo báo cáo feedback dạng PDF theo ngày bắt đầu và ngày kết thúc"""
#         return generate_pdf_report(data)