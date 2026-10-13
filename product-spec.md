# Dealer tracker specification
User: a small dealer practising stock and enquiry management.
Problem: stock status and follow-up tasks are scattered.
Behaviour: add/edit/search/archive/restore stock; change status; record enquiries; complete/reopen follow-ups; view counts and unsold stock value.
Acceptance: valid records persist; invalid fields fail; unknown IDs return 404; archived vehicles cannot receive new enquiries; messages render as text; price is stored in integer pence.
Non-goals: payments, actual customer data, marketplace publishing, valuation, authentication in the local demo.
Public demo data is fictional. Before real use add access controls, backups and abuse protection.
