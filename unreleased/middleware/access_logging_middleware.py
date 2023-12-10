# -*- coding: utf-8 -*-

# import logging

# from loguru import logger
# from starlette.middleware.base import BaseHTTPMiddleware


# class AccessLoggerMiddleware(BaseHTTPMiddleware):
#     """
#     Middleware to log all requests made to application
#     """

#     def __init__(self, app, user_identifier: str = "id"):
#         super().__init__(app)
#         self.user_identifier = user_identifier

#     async def dispatch(self, request, call_next):
#         response = await call_next(request)
#         method = request.method
#         url = request.url
#         client = request.client.host
#         referer = None
#         # if "x-real-ip" in request.headers:
#         #     real_ip = request.headers["x-real-ip"]
#         #     logger.critical(real_ip)
#         headers = request.headers.items()
#         logger.critical(headers)
#         for k, v in headers:
#             logger.debug(f"request key: {k} | value: {v}")
#         logger.debug(f"full request: {request.headers}")

#         if "referer" in request.headers:
#             referer = request.headers["referer"]

#         if self.user_identifier in request.session:
#             user_id = request.session[self.user_identifier]
#         else:
#             user_id = "unknown guest"

#         # ignore favicon requests and log all access requests
#         if "favicon.ico" not in str(url):
#             logging.info(
#                 f"Request Method: {method.upper()} request via {url}\
#                      via referer {referer} accessed from {client} by {user_id} "
#             )
#             logging.debug(f"full_request_data: {dict(request)}")
#         return response
