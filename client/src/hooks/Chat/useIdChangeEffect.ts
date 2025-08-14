import { useEffect, useRef } from 'react';
import { useResetRecoilState, useSetRecoilState } from 'recoil';
import { logger } from '~/utils';
import store from '~/store';

/**
 * Hook to reset visible artifacts when the conversation ID changes
 * @param conversationId - The current conversation ID
 */
export default function useIdChangeEffect(conversationId: string) {
  const lastConvoId = useRef<string | null>(null);
  const resetVisibleArtifacts = useResetRecoilState(store.visibleArtifacts);
  const setIsNavigating = useSetRecoilState(store.isNavigatingAtom);

  useEffect(() => {
    if (conversationId !== lastConvoId.current) {
      logger.log('conversation', 'Conversation ID change');
      resetVisibleArtifacts();
      // Reset navigation state when conversation ID changes
      setIsNavigating(false);
    }
    lastConvoId.current = conversationId;
  }, [conversationId, resetVisibleArtifacts, setIsNavigating]);

  // Fallback: Reset navigation state after a timeout to prevent stuck states
  useEffect(() => {
    const timeout = setTimeout(() => {
      setIsNavigating(false);
    }, 3000); // 3 second fallback - shorter timeout

    return () => clearTimeout(timeout);
  }, [conversationId, setIsNavigating]);

  // Additional fallback: Reset navigation state when component unmounts
  useEffect(() => {
    return () => {
      setIsNavigating(false);
    };
  }, [setIsNavigating]);
}
