"use client";

import { useState } from "react";
import Link from "next/link";
import "./Contact.css";

export default function Contact() {
  const [form, setForm] = useState({ name: "", email: "", message: "" });
  const [sent, setSent] = useState(false);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = (e) => {
    e.preventDefault();
    setSent(true);
  };

  return (
    <div className="page" style={{ backgroundImage: "url(/water.jpg)" }}>
      <div className="overlay"></div>

      <div className="content form-container">
        <h2>Contact Us</h2>
        <p className="contact-sub">Questions about the sensor setup or the ML model? Send a message.</p>

        <form onSubmit={handleSubmit}>
          <input
            type="text"
            name="name"
            placeholder="Your Name"
            value={form.name}
            onChange={handleChange}
            required
          />
          <input
            type="email"
            name="email"
            placeholder="Your Email"
            value={form.email}
            onChange={handleChange}
            required
          />
          <textarea
            name="message"
            placeholder="Your Message"
            value={form.message}
            onChange={handleChange}
            required
          ></textarea>

          <button type="submit">Send Message</button>
        </form>

        {sent && <p className="result">Message ready to send ✅ — we&apos;ll get back to you soon.</p>}

        <div className="contact-links">
          <Link href="/about" className="btn ghost">About the Project</Link>
          <Link href="/dashboard" className="btn ghost">Live Dashboard</Link>
        </div>
      </div>
    </div>
  );
}
