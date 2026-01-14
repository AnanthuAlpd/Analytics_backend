# from db import db

# class MonthlySalesStatsPredicted(db.Model):
#     __tablename__ = 'monthly_sales_stats_predicted'

#     stats_id = db.Column(
#         db.BigInteger,
#         primary_key=True,
#         autoincrement=True
#     )

#     product_id = db.Column(
#         db.BigInteger,
#         db.ForeignKey('products.product_id'),
#         nullable=True,
#         index=True
#     )

#     report_date = db.Column(
#         db.DateTime,
#         nullable=True,
#         index=True
#     )

#     forecasted_quantity = db.Column(
#         db.Float,
#         nullable=True
#     )

#     best_model = db.Column(
#         db.Text,
#         nullable=True
#     )

#     test_mae = db.Column(
#         db.Float,
#         nullable=True
#     )

#     test_rmse = db.Column(
#         db.Float,
#         nullable=True
#     )

#     validation_mae = db.Column(
#         db.Float,
#         nullable=True
#     )

#     def __repr__(self):
#         return (
#             f"<MonthlySalesStatsPredicted "
#             f"stats_id={self.stats_id}, "
#             f"product_id={self.product_id}, "
#             f"report_date={self.report_date}>"
#         )
