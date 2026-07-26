import "../index.css";
import "../App.css";
import AppShell from "../components/AppShell";

export const metadata = {
  title: "Water Quality System",
  description:
    "Real-time water quality monitoring and ML-based prediction powered by ESP32 sensors.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
