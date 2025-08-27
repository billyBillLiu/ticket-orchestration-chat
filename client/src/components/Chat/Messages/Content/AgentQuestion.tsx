import React, { useState } from 'react';
import { Button } from '~/components/ui';
import { useLocalize } from '~/hooks';
import { cn } from '~/utils';

interface AgentQuestionProps {
  question: {
    text: string;
    field_name: string;
    item_index: number;
    field_type: string;
    options?: string[];
  };
  session_id: string;
  conversation_id: string;
  onAnswer: (answer: string) => void;
}

export default function AgentQuestion({ question, session_id, conversation_id, onAnswer }: AgentQuestionProps) {
  const [answer, setAnswer] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const localize = useLocalize();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!answer.trim()) return;

    setIsSubmitting(true);
    try {
      const response = await fetch(`/api/conversations/${conversation_id}/agent-answer`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id,
          question,
          answer: answer.trim(),
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to submit answer');
      }

      const result = await response.json();
      
      // Call the onAnswer callback to update the UI
      onAnswer(result.content);
      
      // Force a page refresh to show the next question or completion
      window.location.reload();
    } catch (error) {
      console.error('Error submitting answer:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderInput = () => {
    switch (question.field_type) {
      case 'bool':
        return (
          <div className="flex gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => setAnswer('true')}
              className={cn(answer === 'true' && 'bg-blue-500 text-white')}
            >
              Yes
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => setAnswer('false')}
              className={cn(answer === 'false' && 'bg-blue-500 text-white')}
            >
              No
            </Button>
          </div>
        );
      
      case 'choice':
        return (
          <select
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            className="w-full p-2 border rounded-md"
          >
            <option value="">Select an option...</option>
            {question.options?.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        );
      
      case 'date':
        return (
          <input
            type="date"
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            className="w-full p-2 border rounded-md"
          />
        );
      
      case 'time':
        return (
          <input
            type="time"
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            className="w-full p-2 border rounded-md"
          />
        );
      
      case 'int':
        return (
          <input
            type="number"
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            className="w-full p-2 border rounded-md"
            placeholder="Enter a number"
          />
        );
      
      default:
        return (
          <textarea
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            className="w-full p-2 border rounded-md min-h-[80px]"
            placeholder="Enter your answer..."
          />
        );
    }
  };

  return (
    <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 my-2">
      <div className="mb-3">
        <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-1">
          {localize('com_ui_agent_question')}
        </h4>
        <p className="text-blue-800 dark:text-blue-200">{question.text}</p>
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-3">
        {renderInput()}
        
        <div className="flex gap-2">
          <Button
            type="submit"
            disabled={!answer.trim() || isSubmitting}
            className="bg-blue-600 hover:bg-blue-700 text-white"
          >
            {isSubmitting ? localize('com_ui_submitting') : localize('com_ui_submit')}
          </Button>
        </div>
      </form>
    </div>
  );
}
