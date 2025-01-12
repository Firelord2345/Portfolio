from flask import Flask, render_template, request, url_for, flash, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor, CKEditorField
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reviews.db'  # SQLite Database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable Flask-SQLAlchemy modification tracking
Bootstrap(app)
ckeditor = CKEditor(app)
db = SQLAlchemy(app)

# Define the Review model (Table)
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    review = db.Column(db.Text, nullable=False)

# Create the database (Run this once to create the tables)
with app.app_context():
    db.create_all()

# Flask-WTF Form Class for Contact
class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        try:
            send_email(form.name.data, form.email.data, form.phone.data, form.message.data)
            flash('Your message has been sent successfully!', 'success')
            return redirect(url_for('contact'))
        except Exception as e:
            flash('An error occurred while sending your message. Please try again.', 'danger')
            print(f"Error: {e}")
    return render_template('contact.html', form=form)

# Email sending function (Traditional method using smtplib)
def send_email(name, email, phone, message):
    sender_email = 'joelroyskroys@gmail.com'
    recipient_email = 'joelroyskroys@gmail.com'
    subject = "New Contact Form Message"
    body = f"Name: {name}\nEmail: {email}\nPhone: {phone}\nMessage:\n{message}"
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, 'ggms acnw sjdf hyty')  # Use app password here if 2FA enabled
            server.sendmail(sender_email, recipient_email, msg.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

# Flask-WTF Form with CKEditor for Reviews
class ReviewForm(FlaskForm):
    name = StringField("Your Name", validators=[DataRequired()])
    email = StringField("Your Email", validators=[DataRequired(), Email()])
    review = CKEditorField("Your Review", validators=[DataRequired()])
    submit = SubmitField("Submit Review")

@app.route("/project", methods=["GET", "POST"])
def project():
    form = ReviewForm()
    if form.validate_on_submit():
        # Insert review into the database
        new_review = Review(name=form.name.data, email=form.email.data, review=form.review.data)
        db.session.add(new_review)
        db.session.commit()
        flash("Thank you for your review!", "success")
        return redirect(url_for("project"))

    # Fetch all reviews from the database
    reviews = Review.query.all()
    return render_template("project.html", form=form, reviews=reviews)

# Define a route for the home page
@app.route("/")
def home():
    current_year = datetime.datetime.now().year 
    return render_template("index.html", current_year=current_year)

# Define a route for the about page
@app.route("/about")
def about():
    current_year = datetime.datetime.now().year 
    return render_template("about.html", current_year=current_year)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
