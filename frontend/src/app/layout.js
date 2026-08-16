import { Inter, IBM_Plex_Sans } from "next/font/google";
import "./globals.css";
import { Toaster } from "react-hot-toast";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const ibmPlexSans = IBM_Plex_Sans({
  subsets: ["latin"],
  variable: "--font-ibm-plex-sans",
  display: "swap",
});

export const metadata = {
  title: "NewsFoundry",
  description: "Outil pour faciliter les revues de presse avec l'IA",
};

export default function RootLayout({ children }) {
  return (
    <html lang="fr" className={`${inter.variable} ${ibmPlexSans.variable}`}>
      <body>
        {children}
        <Toaster />
      </body>
    </html>
  );
}
