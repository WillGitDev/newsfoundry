"use client";
import { useState } from "react";
import Chat from "@/components/Chat";
import ChatThreadHeader from "@/components/ChatThreadHeader";

export default function ChatThreadWrapper({ chatId }) {
  const [title, setTitle] = useState();

  return (
    <>
      <ChatThreadHeader chatTitle={title} />
      <Chat chatId={chatId} onTitleChange={setTitle} />
    </>
  );
}
