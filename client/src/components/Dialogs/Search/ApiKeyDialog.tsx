import React from 'react';
import { FormProvider } from 'react-hook-form';
import { AuthType } from 'librechat-data-provider';
import ApiKeyDialog from '../ApiKeyDialog';
import { useLocalize } from '~/hooks';

interface SearchApiKeyDialogProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: { apiKey: string }) => void;
  onRevoke: () => void;
  isToolAuthenticated: boolean;
  authTypes?: AuthType[];
  register: any;
  handleSubmit: any;
}

export default function SearchApiKeyDialog({
  isOpen,
  onOpenChange,
  onSubmit,
  onRevoke,
  isToolAuthenticated,
  authTypes = [],
  register,
  handleSubmit,
}: SearchApiKeyDialogProps) {
  const localize = useLocalize();

  return (
    <ApiKeyDialog
      isOpen={isOpen}
      onOpenChange={onOpenChange}
      onSubmit={onSubmit}
      onRevoke={onRevoke}
      isToolAuthenticated={isToolAuthenticated}
      authTypes={authTypes}
      register={register}
      handleSubmit={handleSubmit}
      title={localize('com_ui_web_search_api_key')}
      description={localize('com_ui_web_search_api_key_description')}
    />
  );
}
