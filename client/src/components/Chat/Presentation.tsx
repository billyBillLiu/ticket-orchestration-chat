import { useRecoilValue } from 'recoil';
import { useEffect } from 'react';
import { FileSources, LocalStorageKeys } from 'librechat-data-provider';
import type { ExtendedFile } from '~/common';
import { useDeleteFilesMutation } from '~/data-provider';
import DragDropWrapper from '~/components/Chat/Input/Files/DragDropWrapper';
import Artifacts from '~/components/Artifacts/Artifacts';
import { useSetFilesToDelete } from '~/hooks';
import { EditorProvider } from '~/Providers';
import store from '~/store';

export default function Presentation({ children }: { children: React.ReactNode }) {
  const artifacts = useRecoilValue(store.artifactsState);
  const artifactsVisibility = useRecoilValue(store.artifactsVisibility);

  const setFilesToDelete = useSetFilesToDelete();

  const { mutateAsync } = useDeleteFilesMutation({
    onSuccess: () => {
      console.log('Temporary Files deleted');
      setFilesToDelete({});
    },
    onError: (error) => {
      console.log('Error deleting temporary files:', error);
    },
  });

  useEffect(() => {
    const filesToDelete = localStorage.getItem(LocalStorageKeys.FILES_TO_DELETE);
    const map = JSON.parse(filesToDelete ?? '{}') as Record<string, ExtendedFile>;
    const files = Object.values(map)
      .filter(
        (file) =>
          file.filepath != null && file.source && !(file.embedded ?? false) && file.temp_file_id,
      )
      .map((file) => ({
        file_id: file.file_id,
        filepath: file.filepath as string,
        source: file.source as FileSources,
        embedded: !!(file.embedded ?? false),
      }));

    if (files.length === 0) {
      return;
    }
    mutateAsync({ files });
  }, [mutateAsync]);



  return (
    <DragDropWrapper className="relative flex w-full grow overflow-hidden bg-presentation">
      <div className="flex h-full w-full">
        <main className="flex h-full flex-1 flex-col overflow-y-auto" role="main">
          {children}
        </main>
        {artifactsVisibility === true && Object.keys(artifacts ?? {}).length > 0 && (
          <div className="w-1/2 border-l border-border-light">
            <EditorProvider>
              <Artifacts />
            </EditorProvider>
          </div>
        )}
      </div>
    </DragDropWrapper>
  );
}
