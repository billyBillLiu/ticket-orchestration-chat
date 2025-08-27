import React from 'react';
import { CheckCircle, Ticket } from 'lucide-react';
import { cn } from '~/utils';

interface Ticket {
  pseudo_id: string;
  service_area: string;
  category: string;
  ticket_type: string;
  title: string;
  form: Record<string, any>;
}

interface AgentTicketResultProps {
  tickets: Ticket[];
  plan: any;
}

export default function AgentTicketResult({ tickets, plan }: AgentTicketResultProps) {
  return (
    <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4 my-2">
      <div className="flex items-center gap-2 mb-3">
        <CheckCircle className="w-5 h-5 text-green-600" />
        <h4 className="font-medium text-green-900 dark:text-green-100">
          Tickets Created Successfully!
        </h4>
      </div>
      
      <div className="space-y-3">
        {tickets.map((ticket, index) => (
          <div
            key={ticket.pseudo_id}
            className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-3"
          >
            <div className="flex items-start gap-3">
              <Ticket className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-mono text-sm bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-2 py-1 rounded">
                    {ticket.pseudo_id}
                  </span>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {ticket.service_area} • {ticket.category}
                  </span>
                </div>
                <h5 className="font-medium text-gray-900 dark:text-gray-100 mb-2">
                  {ticket.title}
                </h5>
                
                {/* Show key form fields */}
                <div className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                  {Object.entries(ticket.form).slice(0, 3).map(([key, value]) => (
                    <div key={key} className="flex gap-2">
                      <span className="font-medium">{key}:</span>
                      <span className="truncate">{String(value)}</span>
                    </div>
                  ))}
                  {Object.keys(ticket.form).length > 3 && (
                    <div className="text-xs text-gray-500">
                      +{Object.keys(ticket.form).length - 3} more fields
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-4 pt-3 border-t border-green-200 dark:border-green-800">
        <p className="text-sm text-green-800 dark:text-green-200">
          {tickets.length} ticket{tickets.length !== 1 ? 's' : ''} created successfully. 
          The tickets have been submitted to the system.
        </p>
      </div>
    </div>
  );
}
