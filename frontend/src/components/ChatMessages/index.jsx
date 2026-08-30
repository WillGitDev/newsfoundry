import styles from "./chatMessages.module.css";
import ChatMessageBubble from "@components/ChatMessageBubble";

export default function ChatMessages({ messages }) {
  return (
    // A revoir ce code pour les trois vues qui vont switché.
    <>
      {[...messages].reverse().map((msg, index) => (
        <ChatMessageBubble
          key={index}
          role={msg.role}
          content={msg.content}
          timestamp={msg.timestamp}
        />
      ))}
    </>
  );
}
