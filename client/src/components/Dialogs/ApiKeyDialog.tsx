import React from 'react';
import { useFormContext } from 'react-hook-form';
import { AuthType } from 'librechat-data-provider';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '~/components/ui/Dialog';
import { Button } from '~/components/ui/Button';
import { Input } from '~/components/ui/Input';
import { Label } from '~/components/ui/Label';
import { useLocalize } from '~/hooks';

interface ApiKeyDialogProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: { apiKey: string }) => void;
  onRevoke: () => void;
  isToolAuthenticated: boolean;
  isUserProvided?: boolean;
  authTypes?: AuthType[];
  title?: string;
  description?: string;
  register?: any;
  handleSubmit?: any;
}

export default function ApiKeyDialog({
  isOpen,
  onOpenChange,
  onSubmit,
  onRevoke,
  isToolAuthenticated,
  isUserProvided = false,
  authTypes = [],
  title,
  description,
  register,
  handleSubmit,
}: ApiKeyDialogProps) {
  const localize = useLocalize();
  const formContext = useFormContext();
  const formRegister = register || formContext.register;
  const formHandleSubmit = handleSubmit || formContext.handleSubmit;
  const { formState: { errors } } = formContext;

  const handleFormSubmit = (data: any) => {
    onSubmit(data);
  };

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>
            {title || localize('com_ui_enter_api_key')}
          </DialogTitle>
        </DialogHeader>
        <form onSubmit={formHandleSubmit(handleFormSubmit)} className="space-y-4">
          <div>
            <Label htmlFor="apiKey">
              {localize('com_ui_api_key')}
            </Label>
            <Input
              id="apiKey"
              type="password"
              {...formRegister('apiKey', { required: true })}
              placeholder={localize('com_ui_enter_api_key')}
            />
            {errors.apiKey && (
              <p className="text-sm text-red-500">
                API Key is required
              </p>
            )}
          </div>
          {description && (
            <p className="text-sm text-gray-600">
              {description}
            </p>
          )}
          <div className="flex justify-end space-x-2">
            {isToolAuthenticated && (
              <Button
                type="button"
                variant="outline"
                onClick={onRevoke}
              >
                Revoke Key
              </Button>
            )}
            <Button type="submit">
              {localize('com_ui_submit')}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
