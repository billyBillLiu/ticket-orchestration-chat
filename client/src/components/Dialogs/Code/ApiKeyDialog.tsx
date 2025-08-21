import React from 'react';
import { FormProvider } from 'react-hook-form';
import { AuthType } from 'librechat-data-provider';
import ApiKeyDialog from '../ApiKeyDialog';
import { useLocalize } from '~/hooks';

interface CodeApiKeyDialogProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: { apiKey: string }) => void;
  onRevoke: () => void;
  isToolAuthenticated: boolean;
  isUserProvided?: boolean;
  register: any;
  handleSubmit: any;
}

export default function CodeApiKeyDialog({
  isOpen,
  onOpenChange,
  onSubmit,
  onRevoke,
  isToolAuthenticated,
  isUserProvided = false,
  register,
  handleSubmit,
}: CodeApiKeyDialogProps) {
  const localize = useLocalize();

  return (
    <ApiKeyDialog
      isOpen={isOpen}
      onOpenChange={onOpenChange}
      onSubmit={onSubmit}
      onRevoke={onRevoke}
      isToolAuthenticated={isToolAuthenticated}
      isUserProvided={isUserProvided}
      register={register}
      handleSubmit={handleSubmit}
      title={localize('com_assistants_code_interpreter_api_key')}
      description={localize('com_assistants_code_interpreter_api_key_description')}
    />
  );
}
