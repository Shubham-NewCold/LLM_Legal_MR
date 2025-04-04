# test_chunking.py
import os
import sys

# --- Add parent directory to sys.path to find config and document_processing ---
# Adjust the number of '..' based on your project structure if test_chunking.py
# is not directly in the root or a sibling directory to document_processing
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
# --- End Path Adjustment ---

from document_processing.parser import pyparse_hierarchical_chunk_text

# --- Sample Text (Unchanged) ---
sample_text = """
18.3 The Customer shall procure that its Representatives, when visiting the Warehouse, comply with
NewCold's reasonable security and safety procedures and rules in place at the Warehouse,
provided that such security and safety procedures are specified in the Operating Specification
or have been notified in advance to the Customer in writing.
18.4 NewCold shall ensure that full accurate and proper records are kept relating to the provision of
the Services (including details of Products delivered to and despatched from the Warehouse)
and the Charges. All such records must be kept up-to-date and contain information which is
current and accurate. Records shall be kept for a minimum period of six (6) years from (as the
case may be) such Products being Delivered out of NewCold's Custody or such Charges being
invoiced. NewCold shall make such documentation available for examination and copying by
the Customer and its Representatives at any time during such period on reasonable notice.
Notwithstanding the foregoing, NewCold shall not be obliged to disclose any commercially
sensitive or confidential information about its business, its other customers or their businesses.
18.5 Nothing in this Clause 18 shall give the Customer access to any records of NewCold to the
extent that they concern third party goods or products stored at the Warehouse, or any other
Confidential Information of NewCold or any third party.
19. Liability
19.1 Nothing in this Agreement shall be deemed to limit or exclude the liability of a party (the
"Defaulting Party") for:
(a) death or personal injury caused by the Defaulting Party's wilful act, negligence or default
or the wilful act, negligence or default of the Defaulting Party's Representatives;
(b) fraud or fraudulent misrepresentation of the Defaulting Party or its Representatives; or
(c) any other type of liability which cannot be validly limited or excluded at law.
19.2 Subject to Clause 19.1, neither party will be liable, whether in contract, tort (including
negligence), breach of statutory duty, under any indemnity or otherwise in connection with or
arising from this Agreement for any:
(a) loss of profits, revenues or business opportunities;
(b) depletion of goodwill or loss of reputation;
(c) loss of actual or anticipated savings; or
(d) any indirect or consequential loss;
save that nothing in this Clause 19.2 shall relieve Customer of its obligations to make payments
in accordance with this Agreement (including without limitation Customer's obligation to make
DocuSign Envelope ID: 9A2C0839-E078-423C-8685-3D4E052CE25B
20
the Minimum Annual Storage Revenue payments) or any liability of the Customer in connection
with Minimum Storage Requirement.
19.3 NewCold shall have no liability:
(a) for any loss of or damage to Products for which it would otherwise have been liable
unless it is advised in writing of such loss or damage by the Customer within 6 months
of the date on which the Customer was, or ought reasonably to have been, aware of
that loss or damage; or
(b) for any shortfall of Products contained within sealed containers or packaging, which
NewCold collected from the Customer or which were delivered to NewCold and which
have remained in such packaging without being tampered with or replaced.
19.4 Subject to Clause 19.1 but notwithstanding any other provision of this Agreement, NewCold’s
total aggregate liability, whether in contract, tort (including negligence), breach of statutory duty,
under any indemnity or otherwise in connection with or arising from this Agreement shall be
limited:
(a) for liability arising in connection with a failure to meet the Intended Services
Commencement Date, to the costs specified in Clause 3.3 subject to the caps specified
in that Clause;
(b) for costs arising from loss of or damage to Products, to the manufacturing costs and
reasonable and evidenced disposal cost of the Products;
(c) for failure to comply with the Minimum Performance Targets, to the service credits
calculated in accordance with Schedule 4 Part 3 (Service Credits) and the Customer’s
right of termination in accordance with Clause 26.3; and
(d) in aggregate for all liabilities arising under this Agreement in the sum of $10,000,000
(ten million Australian dollars), save that such aggregate cap shall not apply to
NewCold's liability for costs arising from loss of or damage to Products (which shall only
be limited in accordance with Clause 19.4(b)).
19.5 The Customer acknowledges that NewCold's Charges are predicated on the exclusions and
limitations of liability set out in this Clause 19 and the levels of insurance cover specified in
Clause 20.
19.6 Subject to the Customer using its reasonable endeavours to mitigate any such loss or damage,
NewCold shall indemnify the Customer against all losses and damages suffered by the
Customer as a direct result of:
(a) the wilful act, negligence or default of NewCold or its Representatives; or
(b) damage to, destruction or loss of Products at the Warehouse during the period from
when such Products are Delivered into NewCold's Custody until such Products are
Delivered out of NewCold's Custody, such loss and damage to include the direct
manufacturing and disposal costs of such Products.
20. Insurance
20.1 NewCold shall take out and maintain throughout the Term (and for at least 12 months after the
Term has ended) adequate and proper insurance with reputable insurers (which complies with
all applicable statutory requirements) in respect of:
DocuSign Envelope ID: 9A2C0839-E078-423C-8685-3D4E052CE25B
21
(a) employer's liability for all of its personnel who perform any obligations of NewCold under
this Agreement to the extent required by law;
(b) public liability insurance with a minimum indemnity limit of $10,000,000 in respect of
any one occurrence, against the legal liability for death of or bodily injury to persons,
and/or damage to or loss of destruction of any property (including damage to or the loss
or destruction of the Products) arising out of or in connection with the provision by
NewCold or its Representatives of the Services;
(c) motor vehicle liability insurance providing third party property damage cover with a
minimum indemnity limit of $10,000,000 in respect of any one occurrence where the
limit is not otherwise governed by legislation, and NewCold will ensure that any
contractors or subcontractors have a similar policy in place; and
(d) Logistics liability insurance with a minimum indemnity limit of $8,000,000 in respect of
any one occurrence against any damage to or the loss or destruction of any Products
stored at NewCold arising out of or in connection with the provision by NewCold or its
Representatives of the Services.
20.2 The Customer is responsible for insuring the Products against all risks to their full insurable
value.
20.3 Each party shall inform the other as soon as reasonably practicable (and in any event within 5
Business Days of the relevant occurrence) of the occurrence of any event connected with the
Services which could give rise to either party making an insurance claim under NewCold's
insurance policy. If the Customer is claiming under any insurance policy of NewCold, the
Customer shall provide such assistance as NewCold may reasonably require in order to
progress the claim. NewCold will keep the Customer regularly informed of the progress of any
such claim.
20.4 On receipt of the Customer's reasonable written request from time to time, NewCold shall
promptly provide to the Customer:
(a) written details or copies of the insurance policies it is required to maintain pursuant to
Clause 20.1; and
(b) written evidence, reasonably satisfactory to the Customer, of the continuing validity of
such insurance policies and that all premiums payable in respect of such insurance
have been paid and are up to date.
21. Service Credits
21.1 Except for the Initial Period, throughout the duration of the Agreement and subject to the terms
of this Agreement, the Services will be provided so as to satisfy all the Standard KPIs, subject
always to Clause 23.
21.2 Failure by NewCold to meet the Standard KPIs shall give rise to service credits in accordance
with Schedule 4 Part 3 (Service Credits).
21.3 The parties acknowledge that the service credits specified in Schedule 4 Part 3 (Service Credits)
are a reasonable pre-estimate of the actual loss that may be suffered by the Customer as a
result of NewCold's failure to meet the Standard KPIs.
22. Disaster Recovery
22.1 NewCold shall, within 30 days of the Services Commencement Date, put in place in accordance
with the provisions of Schedule 7 a customary and commercially reasonable plan of the
business continuity and recovery procedures to be followed by NewCold in the event of a
Disaster (as such term is defined in Clause 22.2 below) ("Disaster Recovery Plan"). The
Disaster Recovery Plan shall be such as to meet any reasonable requirement set by the
DocuSign Envelope ID: 9A2C0839-E078-423C-8685-3D4E052CE25B
22
Customer and shall be designed to ensure that as far as reasonably practicable despite any
Disaster or Force Majeure Event, the Services continue to be performed without interruption or
derogation and in accordance with this Agreement.
22.2 If NewCold becomes aware of any event or circumstance which has or may lead to
circumstances likely to affect NewCold's ability to provide all or part of the Services (which is
likely to have a material impact for the Customer) in accordance with this Agreement (a
"Disaster"), it shall (save where the event is a Force Majeure Event to which the notice
provisions in Clause 23 apply instead) notify the Customer as soon as practicable and indicate
the expected duration of such effect.
22.3 For the avoidance of doubt, the development of and compliance with the Disaster Recovery
Plan does not relieve NewCold of any of its obligations under this Agreement.
23. Force Majeure
23.1 Neither the Customer nor NewCold will be liable to the other for any delay, hindrance or failure
to comply with all or any of its obligations under this Agreement (save for an obligation to pay
money) to the extent that such delay, hindrance or failure is attributable to a Force Majeure
Event, provided that:
(a) the party affected by the Force Majeure Event (the "Affected Party") as soon as
possible and in any event within 3 Business Days after commencement of the Force
Majeure Event, notifies the other party (the "Non Affected Party") in writing of the
Force Majeure Event. Such notice shall state the effects of the Force Majeure Event on
the Affected Party's ability to perform its obligations under the Agreement and contain
an estimate as to how long the Affected Party believes the Force Majeure Event will
continue; and
(b) the Affected Party uses all reasonable endeavours to mitigate the effect of the Force
Majeure Event on the performance of its obligations under this Agreement and to
ensure the continuity of the performance of the Services.
23.2 NewCold shall, within a reasonable period of notifying the Customer of a Force Majeure Event
in accordance with Clause 23.1(a), put forward reasonable proposals to the Customer for
alternative arrangements for performing its obligations under this Agreement. Following
consideration of each proposal made by NewCold together with any reasonable proposals of its
own (which may include allowing a third party to perform the relevant Service on NewCold's
behalf), the Customer may select a proposal which is, in its reasonable opinion, the most
suitable for its requirements. NewCold shall, if reasonably required by the Customer, be obliged
to implement such proposal as soon as reasonably practicable following its selection by the
Customer.
23.3 During the continuation of the Force Majeure Event in which NewCold (but not the Customer)
is an Affected Party, Charges shall remain payable for, and terms of this Agreement still apply
to, the Services which NewCold continues to provide (or the provision of which it procures from
a third party in accordance with the terms of this Agreement) but shall not be payable for
Services to the extent that, due to the Force Majeure Event, they are not provided or procured.
23.4 As soon as reasonably practicable and in any event within 5 Business Days after the cessation
of the Force Majeure Event, the Affected Party shall notify the Non Affected Party in writing of
the cessation of the Force Majeure Event and shall resume performance of the suspended
obligations under this Agreement.
23.5 If a Force Majeure Event causes or results in a partial or complete destruction of the Warehouse,
NewCold and the other NewCold Group Companies will have the option to rebuild or repair the
Warehouse and to procure a third party supplier (or more than one), approved by the Customer,
(such approval not to be unreasonably withheld, conditioned or delayed) and/or a Back-Up
Operator to provide the alternative storage and handling services for the Products provided that:
DocuSign Envelope ID: 9A2C0839-E078-423C-8685-3D4E052CE25B
23
(a) the Customer shall continue to pay the Charges to NewCold for the Services it receives;
(b) the repaired or rebuilt Warehouse shall be completed and the full Services restored
within 24 months of the start of the Force Majeure Event; and
(c) NewCold has provided the Customer with sufficient evidence demonstrating the ability
(including financial ability) and commitment of NewCold to complete the repair or rebuild
within the time period specified.
23.6 Save where Clause 23.5 applies, if the Force Majeure Event continues for more than 9 months,
either party shall be entitled to terminate this Agreement by serving no less than 3 months'
notice in writing to the other party.
23.7 NewCold is not entitled to rely upon this Clause 23 to the extent the effects or impact of the
circumstances in respect of which NewCold seeks to rely could reasonably and ordinarily have
been materially mitigated or avoided by the application of those business practices, methods,
standards, procedures and policies which would reasonably be expected of a competent and
experienced provider of similar services in Victoria.
23.8 In no event shall a Force Majeure Event where Customer is the Affected Party relieve Customer
of its obligations to make payments in accordance with this Agreement, including without
limitation Customer's obligation to make the Minimum Annual Storage Revenue payments even
if Customer is unable to supply Products to the Warehouse due to a Force Majeure Event,
provided that if:
(a) the Customer is unable to utilise some or all of the Minimum Volume due to a Force
Majeure Event; and
(b) the Customer has notified NewCold in writing of the Force Majeure Event, the effects
of the Force Majeure Event on the Customer’s ability to utilise some or all of the
Minimum Volume and an estimate as to how long the Customer believes the Force
Majeure Event will continue,
NewCold shall use reasonable endeavours to find other customers to utilise the storage space
which would have been used by the Customer but for the Force Majeure Event. To the extent
NewCold receives storage income from third parties using the storage space which would
otherwise have been used by the Customer but which is not being used by the Customer due
to the Force Majeure Event and there is no other space available in the Warehouse, the
Minimum Annual Storage Revenue payments payable by the Customer will be reduced by an
amount equal to that storage income. Notwithstanding any other provision of this Agreement,
to the extent NewCold allocates storage space to a third party's products which would otherwise
have been used for the Customer's Products during the estimated period of the Force Majeure
Event (as notified to NewCold by the Customer in accordance with Clause 23.8(b)), NewCold
shall have no liability to the Customer under Clause 7.5 if the duration of the Force Majeure
Event is less than estimated.
24. Dispute Resolution
24.1 Any Dispute under this Agreement shall be treated in accordance with the provisions of this
Clause 24.
24.2 The Customer and NewCold undertake that upon a Dispute arising a senior Representative of
each of the Customer and NewCold, who shall each have authority to settle the Dispute, meet
(either in person or via teleconference) in good faith as soon as reasonably practicable and in
any event no later than 10 Business Days after a written request from either party to the other,
and use all reasonable endeavours to resolve the Dispute.
24.3 If the Dispute cannot be resolved by negotiation as set forth in Clause 24.2 above, then either
party may initiate mediation before a commercial mediator by serving a written demand for
mediation. Mediation shall be conducted within 30 Business Days of written demand and be
DocuSign Envelope ID: 9A2C0839-E078-423C-8685-3D4E052CE25B
24
administered by the Australian Disputes Centre (ADC). The mediation will be conducted in
accordance with ADC Guidelines for Commercial Mediation which set out the procedures to be
adopted, the process of selection of the mediator and the costs involved, and the terms of those
Guidelines are incorporated in this document.
24.4 All negotiations and mediation shall be conducted in strict confidence. Those negotiations and
mediation shall be without prejudice to the rights of the parties and shall not be used in evidence
or referred to in any way without the prior written consent of both parties in any future court
proceedings except in so far as necessary to enforce any compromise agreement entered into
by the parties.
24.5 If the Dispute has not been resolved as a result of negotiations and mediation referred to in
Clauses 24.2 and 24.3 then either party may pursue formal resolution of that dispute pursuant
to Clause 41.
24.6 Nothing in this Clause 24 shall prevent any party from seeking injunctive or other emergency
relief against the other at any time.
25. Confidentiality
25.1 The parties acknowledge that in the course of their performance of this Agreement (and the
negotiation of it or any variation to it) each party ("Discloser") will disclose or make available
to the other party (the "Receiving Party") information about or relating to its business including,
without limitation, information relating to products, prices, work methods, organisation, business
ideas, business strategies, practices, plans, forecasts handling, costs, markets, inventory
information, customers, technology, and operational and administrative systems ("Confidential
Information").
25.2 The Receiving Party will keep the Discloser's Confidential Information strictly confidential and
not disclose any of it to any person save as permitted under this Clause 25. Nothing in this
Clause 25 shall grant the Receiving Party any right or licence over any Confidential Information
of the Discloser.
25.3 The Receiving Party will make available the Discloser's Confidential Information only to its
relevant Representatives (including, in the case of NewCold, its employees, its direct and
indirect shareholders and their respective employees, direct and indirect investors, auditors,
consultants, advisors, bankers and prospective providers of finance or insurance) and the
Customer Group or NewCold Group Companies (as the case may be) on a need to know basis
and all persons to whom the Confidential Information is made available will be made aware of
the strictly confidential nature of the Confidential Information and the restrictions imposed under
this Clause on the use of it and will be bound by similar requirements not to disclose the
Confidential Information. The Receiving Party will be and remains liable for any breach of this
Clause by such persons.
25.4 Clauses 25.2 and 25.3 shall not apply to any Confidential Information for which the Receiving
Party can prove by written records that it:
(a) was lawfully in its possession prior to such disclosure and was not acquired under an
obligation of confidence;
(b) was already in the public domain at the time of disclosure or is or becomes public
knowledge through no fault of the Receiving Party;
(c) is information furnished to the Receiving Party without restriction by any third party
having a bona fide right to do so;
(d) was developed wholly independently by the Receiving Party without reference to
Confidential Information of the Discloser; or
DocuSign Envelope ID: 9A2C0839-E078-423C-8685-3D4E052CE25B
25
(e) is required (and only to the extent required) to be disclosed by the law, court or
regulatory body of any relevant jurisdiction provided (to the extent legally permissible)
prompt written notice of this is given to the Discloser so the Discloser can attempt to
object to such disclosure.
25.5 All Confidential Information shall be returned to the Discloser or destroyed at its direction. The
obligations of confidentiality set out in this Agreement shall survive the termination of this
Agreement in whole or in part for 5 years except in relation to Confidential Information which is
a trade secret, for which the obligations of confidentiality shall be indefinite.
26. Termination
26.1 The Customer shall, subject to Clause 30.1, have the right at any time during the Term to
terminate this Agreement or all or any of the Services with immediate effect or at a later specified
date by giving written notice to NewCold if an Insolvency Event occurs in relation to NewCold.
26.2 The Customer shall, subject to Clause 26.4, Clause 26.5 and Clause 30.1, be entitled to
terminate this Agreement by written notice to NewCold if NewCold commits a material breach
of this Agreement that substantially impacts NewCold’s provision of Services and is not
remedied within 20 Business Days of receipt of a written notice from the Customer specifying
the breach; provided, however, if such breach cannot reasonably be remedied within 20
Business Days and NewCold has commenced and is reasonably proceeding to remedy the
breach, then such period shall be extended for as long as is reasonably necessary for NewCold
to cure the breach, such additional period not to exceed a further 60 Business Days.
26.3 From the end of the Initial Period, if the OLCOT Figure is below 92% for longer than two
consecutive months or any three months in a Forecast Year due solely to fault on the part of
NewCold, the Customer may notify NewCold in writing and NewCold shall have 60 days from
the date of such notice to demonstrate to the Customer's reasonable satisfaction (acting
reasonably and in good faith) that it is able to achieve an OLCOT Figure of at least 92%. If,
solely due to fault on the part of NewCold, NewCold is unable to demonstrate to the Customer's
reasonable satisfaction within such time period that it is able to achieve an OLCOT Figure of at
least 92%, NewCold shall be deemed to be in material breach of this Agreement and the
Customer shall be entitled to terminate the Agreement on not less than 90 days' prior written
notice provided that the Customer delivers such termination notice within 120 days of the date
on which such right arose.
26.4 NewCold shall be entitled to immediately suspend all or any services to be performed under this
Agreement if (i) an Insolvency Event occurs in relation to the Customer or (ii) NewCold has
given the Customer written notice of a failure by the Customer to pay undisputed sums to
NewCold under this Agreement and the Customer fails to cure such payment default within 30
days after written demand from NewCold; provided, however, that no such grace period will be
available should the Customer default twice in its payment obligations under this Agreement in
the preceding 12 months (even if such payments were subsequently made during the grace
period).
26.5 Without prejudice to any other right or remedy it may have, NewCold may terminate this
Agreement with immediate effect or at a later specified date by giving written notice to the
Customer if:
(a) an Insolvency Event occurs in relation to the Customer; or
(b) the Customer commits a material breach of this Agreement which is incapable of
remedy or which is capable of remedy but is not remedied within 60 days of receipt of
a written notice from NewCold specifying the breach;
(c) a Force Majeure Event causes or results in a partial or complete destruction of the
Warehouse; or
DocuSign Envelope ID: 9A2C0839-E078-423C-8685-3D4E052CE25B
26
(d) the Customer fails to select a proposal for the continued provision of the Services in
accordance with Clause 23.2 within a reasonable period (of not more than 20 Business
Days) of such proposals being made to the Customer.
26.6 Each party shall use its reasonable endeavours to mitigate its Losses in the event of any breach
by the other party of its obligations under this Agreement, even where such breach is the subject
of an indemnity under this Agreement. Where, as a result of a breach of the Agreement by one
of the parties to it, the non-defaulting party receives payment under its insurance cover for some
or all of the Losses arising from the breach, such payment shall be taken into account in
commensurately reducing the Losses for which the defaulting party is liable under this
Agreement.
It shall not constitute a breach by any party hereto of any of its obligations under this Agreement
(including but not limited to any breach giving rise to the termination rights under this Clause
26) to the extent such party’s failure to perform its obligations arises as a result of any breach
by another party hereto, or such other party’s suppliers or contractors (or any Representative,
sub-supplier or sub-contractor of any of them), of its obligations under this Agreement.
27. Consequences of termination
27.1 Termination of this Agreement or any of the Services:
(a) will not affect any accrued rights or liabilities of either party at the date of termination
and shall be without prejudice to any other rights or remedies that either party may have
under this Agreement or at law; and
(b) will not affect the continuance in force of any provision of this Agreement to the extent
it is expressed or by implication intended to continue in force after termination, including,
but not limited to, Clause 1 (Definitions and interpretation), Clause 7.9 (Forecast and
Minimum Annual Revenue); Clause 19 (Liability); Clause 21.3 (Service Credits); Clause
23.1 (Force Majeure); Clause 24 (Dispute Resolution); Clause 25 (Confidentiality);
Clause 27 (Consequences of termination); Clause 28 (Invalidity); Clause 29 (Set-Off
and Third Party Rights); Clause 33 (Language); Clause 36 (Entire Agreement); Clause
37 (Announcements); Clause 38 (Waiver); and Clause 40 (Governing Law and
Jurisdiction).
27.2 On termination or expiry of this Agreement for any reason:
(a) each party shall return to the other, as soon as reasonably practicable, all physical and
electronic copies of Confidential Information of the other, except to the extent the other
party requests in writing that such physical or electronic copies be destroyed and/or
deleted; and
(b) at the reasonable request and at the cost of the Customer, NewCold shall co-operate
in good faith and provide reasonable assistance and information required by a new third
party supplier of services (substantially the same as the Services) to the Customer
following the termination of this Agreement.
27.3 On termination of this Agreement by NewCold pursuant to Clause 26.5(a) or Clause 26.5(b),
NewCold may refuse to deliver Products to the Customer until NewCold has been paid in full
for all Charges then due to it (save for any Charges which are subject to a bona fide dispute
between the parties).
28. Invalidity
If at any time any provision (or part of a provision) of this Agreement is or becomes illegal, invalid
or unenforceable in any respect then that shall not affect the legality, validity or enforceability of
any other provision of this Agreement (or the remainder of that provision).
DocuSign Envelope ID: 9A2C0839-E078-423C-8685-3D4E052CE25B
27
29. Set-Off and Third Party Rights
29.1 All payments due under this Agreement shall be made in full without deduction, withholding or
deferment in respect of any set-off or counterclaim.
29.2 The parties to this Agreement do not intend that there be any third party beneficiaries to this
Agreement.
30. Future Financing/Assignment of Rights
30.1 During the Term, NewCold and/or any other NewCold Group Company may periodically elect
to seek financing and/or refinancing (each a "Financing") from third party lenders (each a
"Lender") using this Agreement, the Warehouse or other assets related to them (all such assets
being collectively referred to as the "Assets") as collateral for any such Financing.
30.2 The Customer agrees to cooperate with NewCold and any of NewCold's Group Companies in
connection with any such Financing (all parties acting reasonably and in good faith) at no outof-pocket cost or expense to the Customer, including, amongst other things:
(a) by promptly amending this Agreement in ways agreed between NewCold and the
Customer, both acting reasonably, if requested by a Lender; and/or
(b) promptly entering into a tripartite agreement with, among others, NewCold, any
NewCold Group Company and the relevant Lender under which the Customer agrees:
(i) not to terminate this Agreement whether as a result of an Insolvency Event of
NewCold or any breach by NewCold of this Agreement without first giving the
Lender notice and a period of at least 45 days to remedy the breach or assume
NewCold's rights and obligations under this Agreement; and
(ii) to issue the Lender at the same time as NewCold copies of any notices served
on NewCold under this Agreement;
provided, however, that the Customer shall not be required to amend any pricing terms
or other provisions which have no reasonable relationship to the Financing. The parties
hereby confirm that any assignment (in particular as collateral) of claims under or in
connection with this Agreement is allowed under Applicable Law and permitted under
this Agreement.
30.3 At any time, and from time to time, upon reasonable written request by NewCold, the Customer
shall cooperate with NewCold to provide a certificate addressed to a third party acknowledging
that the Agreement is in full force and effect and there are no defaults on the part of either party
under the Agreement (provided this reflects the actual circumstances as at the date of the
certificate).
31. Transfer of the Agreement and Management Continuity
31.1 Save as otherwise permitted by this Clause 31 neither party shall assign or otherwise dispose
of any of its rights or obligations under this Agreement.
31.2 NewCold may assign, novate or sub-contract any of its rights and obligations under this
Agreement (in whole or in part) to any other NewCold Group Company, provided that:
(a) where such NewCold Group Company is not of a materially lesser financial standing
than NewCold; and
(i) where NewCold assigns or novates any of its rights and obligations to a
NewCold Group Company, NewCold shall notify the Customer in writing in
advance of such assignment or novation (and provide the Customer with
sufficient information about the relevant NewCold Group Company so that the
DocuSign Envelope ID: 9A2C0839-E078-423C-8685-3D4E052CE25B
28
Customer can satisfy itself that it is not of a materially lesser financial standing
than NewCold); and
(ii) where NewCold sub-contracts any of its rights and obligations to a NewCold
Group Company, NewCold shall remain liable for the acts and omissions of the
sub-contractor as fully as if they were the acts and omissions of NewCold; or
(b) if such NewCold Group Company is of a materially lesser financial standing than
NewCold, then NewCold shall either (at its option) obtain the prior consent of the
Customer (such consent not to be unreasonably withheld, delayed or conditioned) or
shall remain liable for the acts and omissions of the NewCold Group Company.
31.3 For the avoidance of doubt, where any of NewCold's rights and obligations are assigned,
novated or sub-contracted to a NewCold Group Company, such NewCold Group Company will
have the same rights as NewCold to assign, novate or sub-contract the Agreement as permitted
by Clause 31.2 subject to the same conditions set out in Clause 31.2.
31.4 NewCold may:
(a) assign its rights (but not its obligations) under this Agreement (in whole or in part) to
any third party which is not a NewCold Group Company or a Lender
(b) assign its rights (but not its obligations) under this Agreement (in whole or in part) to a
Lender, provided that NewCold notifies the Customer in writing in advance of such
assignment; and
(c) novate or sub-contract this Agreement (in whole or in part) to any third party which is
not a NewCold Group Company provided that NewCold obtains the prior written
consent of the Customer (such consent not to be unreasonably withheld, conditioned
or delayed). If no written consent and no written objection is received by NewCold within
21 days of the request for consent, NewCold shall be entitled to issue a further request
for consent and if no written objection is received by NewCold within 7 days of such
further consent request, such consent shall be deemed to have been given in full.
31.5 Where NewCold seeks the Customer’s consent under clause 31.2 or 31.4, NewCold must
provide suitable information about the financial standing and business experience of the
proposed party to the Customer, and must answer all reasonable questions and requests for
information by the Customer in relation to the proposed new party.
31.6 The Customer may assign its rights under this Agreement to a company in the Customer Group
by giving written notice to NewCold provided that:
(a) such assignment shall not relieve the Customer of its obligations under this Agreement
and the Customer shall remain liable for the acts and omissions of the Customer Group
member as fully as if they were the acts and omissions of the Customer; and
(b) if the assignee ceases to be a company in the Customer Group the Customer shall
procure that the assignee immediately assign its rights under this Agreement back to
the Customer or to another company within the Customer's Group.
31.7 Either party may novate its rights and obligations in connection with the sale of all or
substantially all of its business provided that it receives the other party’s prior written consent,
which shall not be unreasonably withheld, conditioned or delayed after taking into account the
competence, creditworthiness and solvency of the party to whom the rights and obligations will
be novated(which, in the case of the novation of NewCold’s rights and obligations, shall be no
less than that of NewCold as at the Signature Date and, in either case, no less than is necessary
to ensure the party to whom the rights and obligations will be novated is capable of meeting the
relevant obligations under this Agreement).
DocuSign Envelope ID: 9A2C0839-E078-423C-8685-3D4E052CE25B
29
32. Sub-contracting
32.1 NewCold is not, as a result of any sub-contracting arrangement, relieved from the performance
of any obligation under this Agreement and will be responsible and liable for all acts and
omissions of a sub-contractor.
33. Language
All notices and other communications relating to or in respect of this Agreement shall be in the
English language.
34. Notices
All notices expressed to be given by any party to this Agreement shall be in writing and shall be
deemed to have been validly given on the date of delivery to the address referred to below, if
delivered by hand, by post or courier. Any notice which would otherwise be deemed to be given
outside the times of 9.30 a.m. and 5.30 p.m. on a normal Business Day shall be deemed to be
given or made at 9.30 a.m. on the next normal Business Day. Either party may change such
details by giving the other notice in accordance with this Clause 34.
Addresses for notices:
NewCold: Abhy Maharaj
Global Chief Commercial Officer & Chief Operating Officer
NewCold Melbourne No. 2 Pty Ltd. 108 Agar Drive, Truganina, Victoria
Customer: Rob Galt
Global Category Leader, Business Services
Simplot Australia Pty. Ltd
Chifley Business Park, 2 Chifley Drive, Mentone, VIC 3194
35. Further Assurance
Each party shall at its own expense use commercially reasonable efforts to do or procure the
doing of all things as may reasonably be required to give full effect to this Agreement including
the execution of all deeds and documents.
36. Entire Agreement
This Agreement represents the whole and only agreement between the parties in relation to the
subject matter of this Agreement and supersedes any previous agreement between the parties
in respect of its subject matter. Neither party shall have any liability or remedy in respect of any
representation, warranty or other statement (other than as set out in this Agreement) being
false, inaccurate or incomplete unless it was made fraudulently. Each party acknowledges that
in entering into this Agreement it has placed no reliance on, nor has any party given any,
representation, warranty, statement or promise relating to the subject matter of this Agreement
other than as set out in this Agreement. Each party irrevocably and unconditionally waives any
right it may have to rescind this Agreement because of breach of any warranty or representation
not contained in this Agreement unless such misrepresentation was made fraudulently.
37. Announcements
37.1 No press release or other public announcement or communication concerning this Agreement
or any part of it or the parties’ relationship shall be made by either party without prior written
consent of the other. Variation
37.2 Subject to Schedule 1 Part 3 (Charges Review Mechanism) and Schedule 3 (Service Change
Procedure), this Agreement may only be varied from time to time with the written agreement of
the authorised representatives of each party. Any variations, supplements or amendments to
this Agreement shall be invalid unless made in writing.
DocuSign Envelope ID: 9A2C0839-E078-423C-8685-3D4E052CE25B
30
38. Waiver
No delay in exercising, non-exercise or partial exercise by any party of any of its rights, powers
or remedies provided by law or under or in connection with this Agreement shall operate as a
waiver or release of that right, power or remedy. Any waiver or release must be specifically
granted in writing signed by the party granting it. The waiver or release shall only operate as a
waiver or release of the particular breach specified and not of further breaches of the same or
any other type, unless expressly stated otherwise.
39. Independence
NewCold is an independent contractor engaged by the Customer to supply the Services.
Nothing in this Agreement shall make either party the legal representative or agent of the other
nor shall either party have the right or authority to assume, create or incur any liability or
obligation of any kind, express or implied, against, in the name of or on behalf of, the other party.
40. Governing Law and Jurisdiction
40.1 This Agreement and any dispute, claim or obligation (whether contractual or non-contractual)
arising out of or in connection with it, its subject matter or formation shall be governed by the
laws of the state of Victoria, Australia.
40.2 The parties each submit to the exclusive jurisdiction of the Courts of the state of Victoria,
Australia and Courts competent to hear appeals from those Courts.
41. Counterparts
This Agreement may be executed in any number of counterparts and by the parties on separate
counterparts, but shall not be effective until each party has executed at least one counterpart.
Each counterpart shall constitute an original of this Agreement, but all the counterparts shall
together constitute one and the same instrument.
42. Participation of the Parties
The parties acknowledge that this Agreement, and all matters contemplated herein, have been
negotiated by the parties and that each party has participated in the drafting and preparation of
this Agreement from the commencement of negotiations at all times through the execution
hereof. If any provision of this Agreement requires judicial or other interpretation, it is agreed
that the court interpreting or construing it shall not apply a presumption that the terms of this
Agreement are to be more strictly construed against one party by reason of the rule of
construction that a document is to be more strictly construed against a party who by itself or
through its agents prepared the document, it being agreed that all parties to this Agreement
participated in the preparation of this Agreement.
43. Legal Fees and Costs
43.1 Except as otherwise provided in this Agreement, each party shall be responsible for and shall
bear its own costs, charges and expenses incurred in connection with the preparation,
completion and maintenance of this Agreement.
"""

# --- Call the parser ---
# Note: pyparse_hierarchical_chunk_text now returns a tuple: (documents, final_stack)
# We only need the documents list for this test script.
# The initial_stack is None because this is the start of processing this text.
documents_list, _ = pyparse_hierarchical_chunk_text(
    full_text=sample_text,
    source_name="sample.txt",
    page_number=1,
    # Pass the expected page-level metadata
    extra_metadata={"customer": "Simplot Australia", "region": "Australia"},
    initial_stack=None # Start with an empty stack for this text block
)

# --- Print the results ---
print(f"Total chunks created: {len(documents_list)}")
for idx, chunk in enumerate(documents_list):
    print(f"\n--- Chunk {idx+1} ---")
    print(chunk.page_content)
    print("Metadata:", chunk.metadata)
    print("-" * 20)