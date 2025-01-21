FROM python:3.9
COPY . /streamlit_millbank
WORKDIR /streamlit_millbank
RUN pip install -r requirements.txt
EXPOSE 8501
ENTRYPOINT ["streamlit","run"]
CMD ["streamlit.py"]