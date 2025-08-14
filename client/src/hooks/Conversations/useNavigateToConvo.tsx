import { useSetRecoilState } from 'recoil';
import { useNavigate } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { QueryKeys, Constants, dataService } from 'librechat-data-provider';
import type { TConversation, TEndpointsConfig, TModelsConfig } from 'librechat-data-provider';
import { buildDefaultConvo, getDefaultEndpoint, getEndpointField, logger } from '~/utils';
import store from '~/store';
import { useNewConvo } from '~/hooks';

const useNavigateToConvo = (index = 0) => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const clearAllConversations = store.useClearConvoState();
  const setSubmission = useSetRecoilState(store.submissionByIndex(index));
  const clearAllLatestMessages = store.useClearLatestMessages(`useNavigateToConvo ${index}`);
  const { hasSetConversation, setConversation } = store.useCreateConversationAtom(index);
  const { switchToConversation } = useNewConvo(index);
  const setIsNavigating = useSetRecoilState(store.isNavigatingAtom);

  const clearNavigationState = () => {
    setTimeout(() => {
      setIsNavigating(false);
    }, 200); // Slightly longer delay to ensure everything is settled
  };

  const fetchFreshData = async (conversation?: Partial<TConversation>) => {
    const conversationId = conversation?.conversationId;
    if (!conversationId) {
      clearNavigationState();
      return;
    }
    try {
      const response = await queryClient.fetchQuery([QueryKeys.conversation, conversationId], () =>
        dataService.getConversationById(conversationId),
      );
      logger.log('conversation', 'Fetched fresh conversation data', response);
      
      // Merge the server response with the original conversation data
      // This ensures we have all required fields while preserving the server data
      const mergedConversationData = {
        ...conversation, // Original conversation data (has endpoint, model, etc.)
        ...response, // Server response data (has messages, title, etc.)
        conversationId: conversationId, // Ensure conversation ID is preserved
      };
      
      // Add debugging
      console.log('Navigation Debug - Setting conversation:', {
        conversationId,
        response,
        originalConversation: conversation,
        mergedConversationData,
        conversationIdFromData: mergedConversationData?.conversationId
      });
      
      // For existing conversations, directly set the conversation without rebuilding
      // This preserves the conversation ID and prevents the race condition
      setConversation(mergedConversationData as TConversation);
      
      navigate(`/c/${conversationId ?? Constants.NEW_CONVO}`, { state: { focusChat: true } });
    } catch (error) {
      console.error('Error fetching conversation data on navigation', error);
      // Ensure navigation state is cleared even on error
      clearNavigationState();
      
      if (conversation) {
        // Fallback to direct setConversation if fetch fails
        try {
          setConversation(conversation as TConversation);
          navigate(`/c/${conversationId}`, { state: { focusChat: true } });
        } catch (navError) {
          console.error('Error in fallback navigation', navError);
          clearNavigationState();
        }
      }
    } finally {
      clearNavigationState();
    }
  };

  const navigateToConvo = (
    conversation?: TConversation | null,
    options?: {
      resetLatestMessage?: boolean;
      currentConvoId?: string;
    },
  ) => {
    if (!conversation) {
      logger.warn('conversation', 'Conversation not provided to `navigateToConvo`');
      return;
    }
    
    // Set navigating state to prevent race conditions
    setIsNavigating(true);
    
    const { resetLatestMessage = true, currentConvoId } = options || {};
    logger.log('conversation', 'Navigating to conversation', conversation);
    hasSetConversation.current = true;
    setSubmission(null);
    if (resetLatestMessage) {
      clearAllLatestMessages();
    }

    let convo = { ...conversation };
    const endpointsConfig = queryClient.getQueryData<TEndpointsConfig>([QueryKeys.endpoints]);
    if (!convo.endpoint || !endpointsConfig?.[convo.endpoint]) {
      /* undefined/removed endpoint edge case */
      const modelsConfig = queryClient.getQueryData<TModelsConfig>([QueryKeys.models]);
      const defaultEndpoint = getDefaultEndpoint({
        convoSetup: conversation,
        endpointsConfig,
      });

      const endpointType = getEndpointField(endpointsConfig, defaultEndpoint, 'type');
      if (!conversation.endpointType && endpointType) {
        conversation.endpointType = endpointType;
      }

      const models = modelsConfig?.[defaultEndpoint ?? ''] ?? [];

      convo = buildDefaultConvo({
        models,
        conversation,
        endpoint: defaultEndpoint,
        lastConversationSetup: conversation,
      });
    }
    clearAllConversations(true);
    queryClient.setQueryData([QueryKeys.messages, currentConvoId], []);
    if (convo.conversationId !== Constants.NEW_CONVO && convo.conversationId) {
      queryClient.invalidateQueries([QueryKeys.conversation, convo.conversationId]);
      fetchFreshData(convo);
    } else {
      // Use switchToConversation for new conversations as well to ensure proper setup
      switchToConversation(
        convo,
        convo as any,
        undefined, // modelsData
        true, // buildDefault - build default for new conversations
        !resetLatestMessage, // keepLatestMessage
        false, // keepAddedConvos
        false, // disableFocus
        false, // disableParams
      );
      navigate(`/c/${convo.conversationId ?? Constants.NEW_CONVO}`, { state: { focusChat: true } });
      clearNavigationState();
    }
  };

  return {
    navigateToConvo,
  };
};

export default useNavigateToConvo;
