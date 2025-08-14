import { v4 } from 'uuid';
import { useCallback, useRef, useEffect } from 'react';
import { useRecoilValue, useSetRecoilState } from 'recoil';
import { Constants, replaceSpecialVars } from 'librechat-data-provider';
import { useChatContext, useChatFormContext, useAddedChatContext } from '~/Providers';
import { useAuthContext } from '~/hooks/AuthContext';
import store from '~/store';

const appendIndex = (index: number, value?: string) => {
  if (!value) {
    return value;
  }
  return `${value}${Constants.COMMON_DIVIDER}${index}`;
};

export default function useSubmitMessage() {
  const { user } = useAuthContext();
  const methods = useChatFormContext();
  const { ask, index, getMessages, setMessages, latestMessage, conversation } = useChatContext();
  const { addedIndex, ask: askAdditional, conversation: addedConvo } = useAddedChatContext();

  const autoSendPrompts = useRecoilValue(store.autoSendPrompts);
  const activeConvos = useRecoilValue(store.allConversationsSelector);
  const setActivePrompt = useSetRecoilState(store.activePromptByIndex(index));
  const isNavigating = useRecoilValue(store.isNavigatingAtom);
  
  // Track if we're ready to submit messages
  const isReadyToSubmit = useRef(true);

  // Reset ready state when navigation completes
  useEffect(() => {
    if (!isNavigating) {
      // Small delay to ensure conversation state is fully updated
      const timeout = setTimeout(() => {
        isReadyToSubmit.current = true;
      }, 100);
      return () => clearTimeout(timeout);
    } else {
      isReadyToSubmit.current = false;
    }
  }, [isNavigating]);

  const submitMessage = useCallback(
    (data?: { text: string }) => {
      if (!data) {
        return console.warn('No data provided to submitMessage');
      }
      
      // Simple check: only prevent submission if we're actively navigating
      if (!isReadyToSubmit.current) {
        console.warn('Waiting for conversation to load...');
        return;
      }
      
      // Get current conversation context
      const currentConversationId = conversation?.conversationId;
      
      // Validate that we have a valid conversation context
      if (!currentConversationId || currentConversationId === Constants.NEW_CONVO) {
        console.warn('No valid conversation context for message submission', {
          currentConversationId,
          conversation
        });
        return;
      }
      
      const rootMessages = getMessages();
      const isLatestInRootMessages = rootMessages?.some(
        (message) => message.messageId === latestMessage?.messageId,
      );
      if (!isLatestInRootMessages && latestMessage) {
        setMessages([...(rootMessages || []), latestMessage]);
      }

      const hasAdded = addedIndex && activeConvos[addedIndex] && addedConvo;
      const isNewMultiConvo =
        hasAdded &&
        activeConvos.every((convoId) => convoId === Constants.NEW_CONVO) &&
        !rootMessages?.length;
      const overrideConvoId = isNewMultiConvo ? v4() : undefined;
      const overrideUserMessageId = hasAdded ? v4() : undefined;
      const rootIndex = addedIndex - 1;
      const clientTimestamp = new Date().toISOString();

      ask({
        text: data.text,
        overrideConvoId: appendIndex(rootIndex, overrideConvoId),
        overrideUserMessageId: appendIndex(rootIndex, overrideUserMessageId),
        clientTimestamp,
      });

      if (hasAdded) {
        askAdditional(
          {
            text: data.text,
            overrideConvoId: appendIndex(addedIndex, overrideConvoId),
            overrideUserMessageId: appendIndex(addedIndex, overrideUserMessageId),
            clientTimestamp,
          },
          { overrideMessages: rootMessages },
        );
      }
      methods.reset();
    },
    [
      ask,
      methods,
      addedIndex,
      addedConvo,
      setMessages,
      getMessages,
      activeConvos,
      askAdditional,
      latestMessage,
      conversation,
    ],
  );

  const submitPrompt = useCallback(
    (text: string) => {
      const parsedText = replaceSpecialVars({ text, user });
      if (autoSendPrompts) {
        submitMessage({ text: parsedText });
        return;
      }

      const currentText = methods.getValues('text');
      const newText = currentText.trim().length > 1 ? `\n${parsedText}` : parsedText;
      setActivePrompt(newText);
    },
    [autoSendPrompts, submitMessage, setActivePrompt, methods, user],
  );

  return { submitMessage, submitPrompt };
}
