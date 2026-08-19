import styles from "./homeChat.module.css";
import Chat from "@components/Chat";
import PastChat from "@components/PastChat";
import NavChat from "@/components/NavChat";

export default function HomeChat() {
  return (
    <div className={styles.container}>
      <PastChat />
      <div className={styles.chatContainer}>
        <NavChat />
        <Chat />
      </div>
    </div>
  );
}
