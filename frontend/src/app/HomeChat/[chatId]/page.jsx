import styles from "./chatId.module.css";
import Chat from "@components/Chat";
import PastChat from "@components/PastChat";
import ChatThreadWrapper from "./ChatThreadWrapper";

export default async function ChatThread({ params }) {
  const { chatId } = await params;

  return (
    <div className={styles.container}>
      <PastChat />
      <div className={styles.chatContainer}>
        <ChatThreadWrapper chatId={chatId} />
      </div>
    </div>
  );
}
