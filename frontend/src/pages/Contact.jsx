import bgImage from "../assets/water.jpg";
import "./Contact.css";

function Contact() {
  return (
    <div
      className="page"
      style={{ backgroundImage: `url(${bgImage})` }}
    >
      <div className="overlay"></div>

      <div className="content form-container">
        <h2>Contact Us</h2>

        <input type="text" placeholder="Your Name" />
        <input type="email" placeholder="Your Email" />
        <textarea placeholder="Your Message"></textarea>

        <button>Send Message</button>
      </div>
    </div>
  );
}

export default Contact;

