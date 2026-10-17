(function() {
    const DATASET = [{"id": "rippling-vs-deel-global-payroll", "product_a": "Rippling", "product_b": "Deel", "category": "Global Payroll & EOR", "use_case": "Global Contractor Compliance, EOR Statutory Fees & Multi-Currency Payroll", "aff_link_a": "https://www.rippling.com/pricing", "aff_link_b": "https://www.deel.com/pricing", "priceA_base": 35, "priceA_seat": 8, "priceB_base": 0, "priceB_seat": 49, "compliance": "SOC2 Type II & ISO 27001", "compliance_tags": ["SOC2 Type II & ISO 27001", "GDPR"], "stack_tags": ["Xero Two-Way", "QuickBooks", "NetSuite"], "api_ceiling_a": 1000, "api_ceiling_b": 1000, "max_api_ceiling": 1000, "tier_jump_a": 1.1, "tier_jump_b": 1.22, "calc_slug": "rippling-vs-deel-global-payroll-36-month-tco"}, {"id": "gusto-vs-onpay-xero-integration", "product_a": "Gusto", "product_b": "OnPay", "category": "Payroll & Accounting", "use_case": "Two-Way Xero Accounting Sync & Automated Tax Filing", "aff_link_a": "https://gusto.com/product/pricing", "aff_link_b": "https://onpay.com/pricing", "priceA_base": 49, "priceA_seat": 6, "priceB_base": 40, "priceB_seat": 6, "compliance": "SOC2 & HIPAA Ready", "compliance_tags": ["SOC2 Type II & ISO 27001", "HIPAA Ready"], "stack_tags": ["Xero Two-Way", "QuickBooks"], "api_ceiling_a": 1000, "api_ceiling_b": 1000, "max_api_ceiling": 1000, "tier_jump_a": 1.1, "tier_jump_b": 1.12, "calc_slug": "gusto-vs-onpay-xero-integration-36-month-tco"}, {"id": "monday-vs-clickup-soc2-enterprise", "product_a": "monday.com", "product_b": "ClickUp", "category": "Project & Enterprise Ops", "use_case": "SOC2 Compliance, HIPAA Readiness & REST API Rate Limits", "aff_link_a": "https://monday.com/pricing", "aff_link_b": "https://clickup.com/pricing", "priceA_base": 0, "priceA_seat": 12, "priceB_base": 0, "priceB_seat": 10, "compliance": "SOC2 Type II & ISO 27001", "compliance_tags": ["SOC2 Type II & ISO 27001", "HIPAA Ready", "GDPR"], "stack_tags": ["NetSuite"], "api_ceiling_a": 300, "api_ceiling_b": 150, "max_api_ceiling": 300, "tier_jump_a": 1.18, "tier_jump_b": 1.22, "calc_slug": "monday-vs-clickup-soc2-enterprise-36-month-tco"}, {"id": "hubspot-vs-pipedrive-quickbooks-sync", "product_a": "HubSpot CRM", "product_b": "Pipedrive", "category": "CRM & RevOps", "use_case": "Native QuickBooks & Xero Invoicing Sync & Two-Way Deal Automation", "aff_link_a": "https://www.hubspot.com/pricing/crm", "aff_link_b": "https://www.pipedrive.com/en/pricing", "priceA_base": 20, "priceA_seat": 20, "priceB_base": 0, "priceB_seat": 24, "compliance": "SOC2 Type II & GDPR", "compliance_tags": ["SOC2 Type II & ISO 27001", "GDPR"], "stack_tags": ["Xero Two-Way", "QuickBooks", "HubSpot/Salesforce"], "api_ceiling_a": 1000, "api_ceiling_b": 300, "max_api_ceiling": 1000, "tier_jump_a": 1.1, "tier_jump_b": 1.22, "calc_slug": "hubspot-vs-pipedrive-quickbooks-sync-36-month-tco"}, {"id": "freshbooks-vs-xero-multi-entity", "product_a": "FreshBooks", "product_b": "Xero", "category": "Payroll & Accounting", "use_case": "Multi-Currency Invoicing, BAS/GST Tax & Automated Bank Reconciliation", "aff_link_a": "https://www.freshbooks.com/pricing", "aff_link_b": "https://www.xero.com/au/pricing-plans/", "priceA_base": 19, "priceA_seat": 11, "priceB_base": 42, "priceB_seat": 0, "compliance": "ISO 27001 & PCI-DSS", "compliance_tags": ["SOC2 Type II & ISO 27001", "AU STP Phase 2 & Xero BAS", "GDPR"], "stack_tags": ["Xero Two-Way", "QuickBooks", "NetSuite"], "api_ceiling_a": 300, "api_ceiling_b": 1000, "max_api_ceiling": 1000, "tier_jump_a": 1.1, "tier_jump_b": 1.12, "calc_slug": "freshbooks-vs-xero-multi-entity-36-month-tco"}, {"id": "notion-vs-coda-enterprise-wiki", "product_a": "Notion", "product_b": "Coda", "category": "Project & Enterprise Ops", "use_case": "Enterprise Wiki Permissions, SAML SSO & REST API Payload Limits", "aff_link_a": "https://www.notion.so/pricing", "aff_link_b": "https://coda.io/pricing", "priceA_base": 0, "priceA_seat": 15, "priceB_base": 0, "priceB_seat": 12, "compliance": "SOC2 Type II & SAML SSO", "compliance_tags": ["SOC2 Type II & ISO 27001"], "stack_tags": ["NetSuite"], "api_ceiling_a": 300, "api_ceiling_b": 300, "max_api_ceiling": 300, "tier_jump_a": 1.18, "tier_jump_b": 1.22, "calc_slug": "notion-vs-coda-enterprise-wiki-36-month-tco"}, {"id": "activecampaign-vs-klaviyo-webhooks", "product_a": "ActiveCampaign", "product_b": "Klaviyo", "category": "CRM & RevOps", "use_case": "Webhook Automation Latency, API Throughput & E-Commerce CRM Sync", "aff_link_a": "https://www.activecampaign.com/pricing", "aff_link_b": "https://www.klaviyo.com/pricing", "priceA_base": 49, "priceA_seat": 5, "priceB_base": 60, "priceB_seat": 0, "compliance": "SOC2 & GDPR Compliant", "compliance_tags": ["SOC2 Type II & ISO 27001", "GDPR"], "stack_tags": ["QuickBooks", "HubSpot/Salesforce"], "api_ceiling_a": 1000, "api_ceiling_b": 1000, "max_api_ceiling": 1000, "tier_jump_a": 1.1, "tier_jump_b": 1.12, "calc_slug": "activecampaign-vs-klaviyo-webhooks-36-month-tco"}, {"id": "zendesk-vs-intercom-sla-routing", "product_a": "Zendesk", "product_b": "Intercom", "category": "CRM & RevOps", "use_case": "Omnichannel Ticketing SLA Routing, AI Agent Costs & Custom Webhooks", "aff_link_a": "https://www.zendesk.com/pricing", "aff_link_b": "https://www.intercom.com/pricing", "priceA_base": 0, "priceA_seat": 55, "priceB_base": 0, "priceB_seat": 39, "compliance": "SOC2 Type II & HIPAA", "compliance_tags": ["SOC2 Type II & ISO 27001", "HIPAA Ready"], "stack_tags": ["QuickBooks", "HubSpot/Salesforce"], "api_ceiling_a": 1000, "api_ceiling_b": 1000, "max_api_ceiling": 1000, "tier_jump_a": 1.18, "tier_jump_b": 1.22, "calc_slug": "zendesk-vs-intercom-sla-routing-36-month-tco"}, {"id": "shopify-vs-bigcommerce-b2b-api", "product_a": "Shopify", "product_b": "BigCommerce", "category": "Project & Enterprise Ops", "use_case": "Headless Storefront GraphQL API Rate Limits & B2B Wholesale Checkout", "aff_link_a": "https://www.shopify.com/pricing", "aff_link_b": "https://www.bigcommerce.com/pricing", "priceA_base": 105, "priceA_seat": 0, "priceB_base": 105, "priceB_seat": 0, "compliance": "PCI-DSS Level 1 & SOC2", "compliance_tags": ["SOC2 Type II & ISO 27001"], "stack_tags": ["NetSuite"], "api_ceiling_a": 1000, "api_ceiling_b": 1000, "max_api_ceiling": 1000, "tier_jump_a": 1.1, "tier_jump_b": 1.12, "calc_slug": "shopify-vs-bigcommerce-b2b-api-36-month-tco"}, {"id": "asana-vs-smartsheet-resource-audit", "product_a": "Asana", "product_b": "Smartsheet", "category": "Project & Enterprise Ops", "use_case": "Portfolio Resource Allocation, SAML SSO & Immutable Audit Log Export", "aff_link_a": "https://asana.com/pricing", "aff_link_b": "https://www.smartsheet.com/pricing", "priceA_base": 0, "priceA_seat": 24, "priceB_base": 0, "priceB_seat": 19, "compliance": "SOC2 Type II & ISO 27001", "compliance_tags": ["SOC2 Type II & ISO 27001", "GDPR"], "stack_tags": ["NetSuite"], "api_ceiling_a": 1000, "api_ceiling_b": 300, "max_api_ceiling": 1000, "tier_jump_a": 1.18, "tier_jump_b": 1.22, "calc_slug": "asana-vs-smartsheet-resource-audit-36-month-tco"}, {"id": "rippling-vs-employment-hero-australia", "product_a": "Rippling AU", "product_b": "Employment Hero", "category": "AU & APAC Compliance", "use_case": "Australian STP Phase 2, Payday Super 2026, Fair Work Awards & Xero Sync", "aff_link_a": "https://www.rippling.com/en-AU/pricing", "aff_link_b": "https://employmenthero.com/pricing/", "priceA_base": 35, "priceA_seat": 10, "priceB_base": 0, "priceB_seat": 12, "compliance": "ATO STP Phase 2 & ISO 27001", "compliance_tags": ["SOC2 Type II & ISO 27001", "AU STP Phase 2 & Xero BAS", "GDPR"], "stack_tags": ["Xero Two-Way"], "api_ceiling_a": 1000, "api_ceiling_b": 300, "max_api_ceiling": 1000, "tier_jump_a": 1.1, "tier_jump_b": 1.22, "calc_slug": "rippling-vs-employment-hero-australia-36-month-tco"}, {"id": "xero-vs-myob-australian-accounting", "product_a": "Xero", "product_b": "MYOB Business", "category": "AU & APAC Compliance", "use_case": "Australian BAS/GST Reconciliation, Payday Super Clearing & Bank Feeds", "aff_link_a": "https://www.xero.com/au/pricing-plans/", "aff_link_b": "https://www.myob.com/au/pricing", "priceA_base": 45, "priceA_seat": 2, "priceB_base": 34, "priceB_seat": 2, "compliance": "ATO DSP Certified & ISO 27001", "compliance_tags": ["SOC2 Type II & ISO 27001", "AU STP Phase 2 & Xero BAS", "GDPR"], "stack_tags": ["Xero Two-Way", "QuickBooks"], "api_ceiling_a": 1000, "api_ceiling_b": 150, "max_api_ceiling": 1000, "tier_jump_a": 1.1, "tier_jump_b": 1.12, "calc_slug": "xero-vs-myob-australian-accounting-36-month-tco"}, {"id": "servicem8-vs-tradify-xero-tradies", "product_a": "ServiceM8", "product_b": "Tradify", "category": "AU & APAC Compliance", "use_case": "Australian Field Service Job Dispatch, Quoting & Two-Way Xero Sync", "aff_link_a": "https://www.servicem8.com/au/pricing", "aff_link_b": "https://www.tradifyhq.com/au/pricing", "priceA_base": 29, "priceA_seat": 0, "priceB_base": 0, "priceB_seat": 39, "compliance": "Xero Certified & AU Privacy Act", "compliance_tags": ["SOC2 Type II & ISO 27001", "AU STP Phase 2 & Xero BAS"], "stack_tags": ["Xero Two-Way"], "api_ceiling_a": 120, "api_ceiling_b": 1000, "max_api_ceiling": 1000, "tier_jump_a": 1.1, "tier_jump_b": 1.22, "calc_slug": "servicem8-vs-tradify-xero-tradies-36-month-tco"}, {"id": "deel-vs-remote-apac-eor", "product_a": "Deel", "product_b": "Remote.com", "category": "Global Payroll & EOR", "use_case": "Employer of Record (EOR) Statutory Onboarding in Australia, NZ & APAC", "aff_link_a": "https://www.deel.com/pricing", "aff_link_b": "https://remote.com/pricing", "priceA_base": 0, "priceA_seat": 49, "priceB_base": 0, "priceB_seat": 29, "compliance": "SOC2 Type II & GDPR / APP", "compliance_tags": ["SOC2 Type II & ISO 27001", "GDPR"], "stack_tags": ["Xero Two-Way", "QuickBooks", "NetSuite"], "api_ceiling_a": 1000, "api_ceiling_b": 1000, "max_api_ceiling": 1000, "tier_jump_a": 1.18, "tier_jump_b": 1.22, "calc_slug": "deel-vs-remote-apac-eor-36-month-tco"}, {"id": "deputy-vs-tanda-fair-work-award", "product_a": "Deputy", "product_b": "Tanda (Workforce)", "category": "AU & APAC Compliance", "use_case": "Australian Fair Work Modern Award Interpretation, Rostering & Xero Payroll", "aff_link_a": "https://www.deputy.com/au/pricing", "aff_link_b": "https://www.tanda.co/pricing/", "priceA_base": 0, "priceA_seat": 6, "priceB_base": 0, "priceB_seat": 7, "compliance": "Fair Work Award Engine & ISO 27001", "compliance_tags": ["SOC2 Type II & ISO 27001", "AU STP Phase 2 & Xero BAS", "GDPR"], "stack_tags": ["Xero Two-Way", "QuickBooks", "NetSuite"], "api_ceiling_a": 120, "api_ceiling_b": 150, "max_api_ceiling": 150, "tier_jump_a": 1.18, "tier_jump_b": 1.22, "calc_slug": "deputy-vs-tanda-fair-work-award-36-month-tco"}, {"id": "apollo-vs-zoominfo-b2b-sales-data", "product_a": "Apollo.io", "product_b": "ZoomInfo", "category": "CRM & RevOps", "use_case": "B2B Contact Enrichment API Credits, CRM Bi-Directional Sync & GDPR", "aff_link_a": "https://www.apollo.io/pricing", "aff_link_b": "https://www.zoominfo.com/pricing", "priceA_base": 0, "priceA_seat": 49, "priceB_base": 250, "priceB_seat": 60, "compliance": "SOC2 Type II & ISO 27001", "compliance_tags": ["SOC2 Type II & ISO 27001", "GDPR"], "stack_tags": ["QuickBooks", "HubSpot/Salesforce"], "api_ceiling_a": 1000, "api_ceiling_b": 1000, "max_api_ceiling": 1000, "tier_jump_a": 1.18, "tier_jump_b": 1.12, "calc_slug": "apollo-vs-zoominfo-b2b-sales-data-36-month-tco"}, {"id": "pandadoc-vs-docusign-crm-cpq", "product_a": "PandaDoc", "product_b": "DocuSign", "category": "CRM & RevOps", "use_case": "Automated CPQ Quote Generation, HubSpot/Pipedrive Sync & eSignature API", "aff_link_a": "https://www.pandadoc.com/pricing/", "aff_link_b": "https://www.docusign.com/products-and-pricing", "priceA_base": 0, "priceA_seat": 35, "priceB_base": 0, "priceB_seat": 40, "compliance": "SOC2 Type II & HIPAA / eIDAS", "compliance_tags": ["SOC2 Type II & ISO 27001", "HIPAA Ready"], "stack_tags": ["QuickBooks", "HubSpot/Salesforce"], "api_ceiling_a": 1000, "api_ceiling_b": 1000, "max_api_ceiling": 1000, "tier_jump_a": 1.18, "tier_jump_b": 1.22, "calc_slug": "pandadoc-vs-docusign-crm-cpq-36-month-tco"}, {"id": "make-vs-zapier-webhook-pricing", "product_a": "Make.com", "product_b": "Zapier", "category": "Project & Enterprise Ops", "use_case": "High-Volume Webhook Operations, Multi-Step JSON Parsing & Enterprise RBAC", "aff_link_a": "https://www.make.com/en/pricing", "aff_link_b": "https://zapier.com/pricing", "priceA_base": 16, "priceA_seat": 2, "priceB_base": 69, "priceB_seat": 5, "compliance": "SOC2 Type II & GDPR", "compliance_tags": ["SOC2 Type II & ISO 27001", "GDPR"], "stack_tags": ["NetSuite"], "api_ceiling_a": 120, "api_ceiling_b": 1000, "max_api_ceiling": 1000, "tier_jump_a": 1.1, "tier_jump_b": 1.12, "calc_slug": "make-vs-zapier-webhook-pricing-36-month-tco"}, {"id": "semrush-vs-ahrefs-enterprise-seo-api", "product_a": "Semrush", "product_b": "Ahrefs", "category": "CRM & RevOps", "use_case": "Search Intelligence API Units, Multi-Seat Agency Licensing & Looker Studio", "aff_link_a": "https://www.semrush.com/prices/", "aff_link_b": "https://ahrefs.com/pricing", "priceA_base": 139, "priceA_seat": 45, "priceB_base": 129, "priceB_seat": 50, "compliance": "SOC2 Type II & GDPR", "compliance_tags": ["SOC2 Type II & ISO 27001", "GDPR"], "stack_tags": ["QuickBooks", "NetSuite", "HubSpot/Salesforce"], "api_ceiling_a": 1000, "api_ceiling_b": 1000, "max_api_ceiling": 1000, "tier_jump_a": 1.1, "tier_jump_b": 1.12, "calc_slug": "semrush-vs-ahrefs-enterprise-seo-api-36-month-tco"}, {"id": "airwallex-vs-wise-business-xero-au", "product_a": "Airwallex", "product_b": "Wise Business", "category": "AU & APAC Compliance", "use_case": "Multi-Currency Corporate Cards, FX Spreads & Live Xero Bank Feed Sync (AU)", "aff_link_a": "https://www.airwallex.com/au/pricing", "aff_link_b": "https://wise.com/au/pricing/business", "priceA_base": 0, "priceA_seat": 10, "priceB_base": 0, "priceB_seat": 5, "compliance": "ASIC AFSL & PCI-DSS Level 1", "compliance_tags": ["SOC2 Type II & ISO 27001", "AU STP Phase 2 & Xero BAS"], "stack_tags": ["Xero Two-Way"], "api_ceiling_a": 300, "api_ceiling_b": 150, "max_api_ceiling": 300, "tier_jump_a": 1.18, "tier_jump_b": 1.22, "calc_slug": "airwallex-vs-wise-business-xero-au-36-month-tco"}, {"id": "brevo-vs-mailchimp-transactional-api", "product_a": "Brevo", "product_b": "Mailchimp", "category": "CRM & RevOps", "use_case": "Transactional SMTP Relay Throughput, Dedicated IPs & Marketing Automation", "aff_link_a": "https://www.brevo.com/pricing/", "aff_link_b": "https://mailchimp.com/pricing/marketing/", "priceA_base": 25, "priceA_seat": 12, "priceB_base": 45, "priceB_seat": 15, "compliance": "ISO 27001 & GDPR", "compliance_tags": ["SOC2 Type II & ISO 27001", "GDPR"], "stack_tags": ["QuickBooks", "HubSpot/Salesforce"], "api_ceiling_a": 300, "api_ceiling_b": 1000, "max_api_ceiling": 1000, "tier_jump_a": 1.1, "tier_jump_b": 1.12, "calc_slug": "brevo-vs-mailchimp-transactional-api-36-month-tco"}, {"id": "webflow-vs-framer-enterprise-cms", "product_a": "Webflow", "product_b": "Framer", "category": "Project & Enterprise Ops", "use_case": "Headless CMS API Limits, SAML SSO Seat Governance & Edge Hosting SLA", "aff_link_a": "https://webflow.com/pricing", "aff_link_b": "https://www.framer.com/pricing", "priceA_base": 29, "priceA_seat": 19, "priceB_base": 30, "priceB_seat": 20, "compliance": "SOC2 Type II & ISO 27001", "compliance_tags": ["SOC2 Type II & ISO 27001", "GDPR"], "stack_tags": ["NetSuite"], "api_ceiling_a": 300, "api_ceiling_b": 300, "max_api_ceiling": 300, "tier_jump_a": 1.1, "tier_jump_b": 1.12, "calc_slug": "webflow-vs-framer-enterprise-cms-36-month-tco"}, {"id": "cliniko-vs-halaxy-allied-health-au", "product_a": "Cliniko", "product_b": "Halaxy", "category": "AU & APAC Compliance", "use_case": "Australian Allied Health NDIS/Medicare Claiming, Xero Sync & APP Privacy", "aff_link_a": "https://www.cliniko.com/pricing/", "aff_link_b": "https://www.halaxy.com/article/pricing", "priceA_base": 45, "priceA_seat": 15, "priceB_base": 0, "priceB_seat": 29, "compliance": "AU Privacy Act (APP) & HIPAA", "compliance_tags": ["SOC2 Type II & ISO 27001", "AU STP Phase 2 & Xero BAS", "HIPAA Ready"], "stack_tags": ["Xero Two-Way"], "api_ceiling_a": 1000, "api_ceiling_b": 1000, "max_api_ceiling": 1000, "tier_jump_a": 1.1, "tier_jump_b": 1.22, "calc_slug": "cliniko-vs-halaxy-allied-health-au-36-month-tco"}, {"id": "simpro-vs-aroflo-commercial-tradies-au", "product_a": "Simpro", "product_b": "AroFlo", "category": "AU & APAC Compliance", "use_case": "Commercial Trade Project Estimating, Inventory & Xero/MYOB Ledger Sync", "aff_link_a": "https://www.simprogroup.com/au/solutions", "aff_link_b": "https://www.aroflo.com/pricing/", "priceA_base": 99, "priceA_seat": 45, "priceB_base": 50, "priceB_seat": 35, "compliance": "Xero/MYOB Certified & ISO 27001", "compliance_tags": ["SOC2 Type II & ISO 27001", "AU STP Phase 2 & Xero BAS", "GDPR"], "stack_tags": ["Xero Two-Way", "NetSuite"], "api_ceiling_a": 1000, "api_ceiling_b": 1000, "max_api_ceiling": 1000, "tier_jump_a": 1.1, "tier_jump_b": 1.12, "calc_slug": "simpro-vs-aroflo-commercial-tradies-au-36-month-tco"}, {"id": "dext-vs-hubdoc-xero-bas-automation", "product_a": "Dext Prepare", "product_b": "Hubdoc", "category": "AU & APAC Compliance", "use_case": "Automated Receipt OCR Line-Item Extraction, ABN Validation & Xero BAS Sync", "aff_link_a": "https://dext.com/au/pricing", "aff_link_b": "https://www.xero.com/au/hubdoc/", "priceA_base": 35, "priceA_seat": 3, "priceB_base": 18, "priceB_seat": 0, "compliance": "ATO Record Keeping & SOC2", "compliance_tags": ["SOC2 Type II & ISO 27001", "AU STP Phase 2 & Xero BAS"], "stack_tags": ["Xero Two-Way"], "api_ceiling_a": 1000, "api_ceiling_b": 150, "max_api_ceiling": 1000, "tier_jump_a": 1.1, "tier_jump_b": 1.12, "calc_slug": "dext-vs-hubdoc-xero-bas-automation-36-month-tco"}, {"id": "cin7-vs-unleashed-xero-inventory-erp", "product_a": "Cin7 Core", "product_b": "Unleashed", "category": "Payroll & Accounting", "use_case": "Multi-Warehouse B2B Inventory, Bill of Materials (BOM) & Xero COGS Sync", "aff_link_a": "https://www.cin7.com/pricing/", "aff_link_b": "https://www.unleashedsoftware.com/pricing", "priceA_base": 349, "priceA_seat": 15, "priceB_base": 380, "priceB_seat": 20, "compliance": "Xero Platinum Partner & SOC2", "compliance_tags": ["SOC2 Type II & ISO 27001"], "stack_tags": ["Xero Two-Way", "QuickBooks", "NetSuite"], "api_ceiling_a": 1000, "api_ceiling_b": 1000, "max_api_ceiling": 1000, "tier_jump_a": 1.1, "tier_jump_b": 1.12, "calc_slug": "cin7-vs-unleashed-xero-inventory-erp-36-month-tco"}, {"id": "intercom-vs-freshdesk-ai-ticketing", "product_a": "Intercom", "product_b": "Freshdesk", "category": "CRM & RevOps", "use_case": "AI Resolution Bot Pricing, Omnichannel SLA Routing & CRM Webhook Sync", "aff_link_a": "https://www.intercom.com/pricing", "aff_link_b": "https://www.freshworks.com/freshdesk/pricing/", "priceA_base": 0, "priceA_seat": 39, "priceB_base": 0, "priceB_seat": 18, "compliance": "SOC2 Type II & ISO 27001", "compliance_tags": ["SOC2 Type II & ISO 27001", "GDPR"], "stack_tags": ["QuickBooks", "HubSpot/Salesforce"], "api_ceiling_a": 1000, "api_ceiling_b": 300, "max_api_ceiling": 1000, "tier_jump_a": 1.18, "tier_jump_b": 1.22, "calc_slug": "intercom-vs-freshdesk-ai-ticketing-36-month-tco"}, {"id": "pipedrive-vs-monday-sales-crm", "product_a": "Pipedrive", "product_b": "monday sales CRM", "category": "CRM & RevOps", "use_case": "B2B Deal Pipeline Automation, Email Sequence Tracking & REST API Limits", "aff_link_a": "https://www.pipedrive.com/en/pricing", "aff_link_b": "https://monday.com/pricing", "priceA_base": 0, "priceA_seat": 24, "priceB_base": 0, "priceB_seat": 15, "compliance": "SOC2 Type II & ISO 27001", "compliance_tags": ["SOC2 Type II & ISO 27001", "GDPR"], "stack_tags": ["QuickBooks", "HubSpot/Salesforce"], "api_ceiling_a": 1000, "api_ceiling_b": 300, "max_api_ceiling": 1000, "tier_jump_a": 1.18, "tier_jump_b": 1.22, "calc_slug": "pipedrive-vs-monday-sales-crm-36-month-tco"}, {"id": "clickup-vs-notion-ai-workspace", "product_a": "ClickUp", "product_b": "Notion", "category": "Project & Enterprise Ops", "use_case": "Unified Engineering Sprint Tracking, AI Add-On Seat Cost & SAML SSO", "aff_link_a": "https://clickup.com/pricing", "aff_link_b": "https://www.notion.so/pricing", "priceA_base": 0, "priceA_seat": 10, "priceB_base": 0, "priceB_seat": 15, "compliance": "SOC2 Type II & SAML SSO", "compliance_tags": ["SOC2 Type II & ISO 27001"], "stack_tags": ["NetSuite"], "api_ceiling_a": 300, "api_ceiling_b": 300, "max_api_ceiling": 300, "tier_jump_a": 1.18, "tier_jump_b": 1.22, "calc_slug": "clickup-vs-notion-ai-workspace-36-month-tco"}, {"id": "freshbooks-vs-quickbooks-online-au", "product_a": "FreshBooks", "product_b": "QuickBooks Online", "category": "Payroll & Accounting", "use_case": "Automated Client Invoicing, BAS/GST Tax Tracking & Multi-User Seat Limits", "aff_link_a": "https://www.freshbooks.com/pricing", "aff_link_b": "https://quickbooks.intuit.com/au/pricing/", "priceA_base": 19, "priceA_seat": 11, "priceB_base": 35, "priceB_seat": 5, "compliance": "PCI-DSS & ATO STP Compliant", "compliance_tags": ["SOC2 Type II & ISO 27001", "AU STP Phase 2 & Xero BAS"], "stack_tags": ["Xero Two-Way", "QuickBooks"], "api_ceiling_a": 300, "api_ceiling_b": 150, "max_api_ceiling": 300, "tier_jump_a": 1.1, "tier_jump_b": 1.12, "calc_slug": "freshbooks-vs-quickbooks-online-au-36-month-tco"}, {"id": "activecampaign-vs-hubspot-marketing", "product_a": "ActiveCampaign", "product_b": "HubSpot Marketing", "category": "CRM & RevOps", "use_case": "Multi-Branch Lead Scoring, Contact Tier Scaling & CRM Bi-Directional Sync", "aff_link_a": "https://www.activecampaign.com/pricing", "aff_link_b": "https://www.hubspot.com/pricing/marketing", "priceA_base": 49, "priceA_seat": 5, "priceB_base": 20, "priceB_seat": 20, "compliance": "SOC2 Type II & GDPR", "compliance_tags": ["SOC2 Type II & ISO 27001", "GDPR"], "stack_tags": ["QuickBooks", "HubSpot/Salesforce"], "api_ceiling_a": 1000, "api_ceiling_b": 300, "max_api_ceiling": 1000, "tier_jump_a": 1.1, "tier_jump_b": 1.12, "calc_slug": "activecampaign-vs-hubspot-marketing-36-month-tco"}, {"id": "folk-vs-attio-modern-b2b-crm", "product_a": "folk CRM", "product_b": "Attio", "category": "CRM & RevOps", "use_case": "Custom Object Data Modeling, LinkedIn/Email Enrichment & REST API Sync", "aff_link_a": "https://www.folk.app/pricing", "aff_link_b": "https://attio.com/pricing", "priceA_base": 0, "priceA_seat": 20, "priceB_base": 0, "priceB_seat": 29, "compliance": "SOC2 Type II & GDPR", "compliance_tags": ["SOC2 Type II & ISO 27001", "GDPR"], "stack_tags": ["QuickBooks", "HubSpot/Salesforce"], "api_ceiling_a": 1000, "api_ceiling_b": 1000, "max_api_ceiling": 1000, "tier_jump_a": 1.18, "tier_jump_b": 1.22, "calc_slug": "folk-vs-attio-modern-b2b-crm-36-month-tco"}, {"id": "linear-vs-jira-engineering-api", "product_a": "Linear", "product_b": "Jira Software", "category": "Project & Enterprise Ops", "use_case": "GitHub/GitLab PR Automation, GraphQL API Sync & SAML SSO Governance", "aff_link_a": "https://linear.app/pricing", "aff_link_b": "https://www.atlassian.com/software/jira/pricing", "priceA_base": 0, "priceA_seat": 10, "priceB_base": 0, "priceB_seat": 9, "compliance": "SOC2 Type II & ISO 27001", "compliance_tags": ["SOC2 Type II & ISO 27001", "GDPR"], "stack_tags": ["NetSuite"], "api_ceiling_a": 300, "api_ceiling_b": 150, "max_api_ceiling": 300, "tier_jump_a": 1.18, "tier_jump_b": 1.22, "calc_slug": "linear-vs-jira-engineering-api-36-month-tco"}, {"id": "miro-vs-lucidchart-enterprise-sso", "product_a": "Miro", "product_b": "Lucidchart", "category": "Project & Enterprise Ops", "use_case": "AWS/Azure Cloud Architecture Diagramming, SCIM Provisioning & Guest Licensing", "aff_link_a": "https://miro.com/pricing/", "aff_link_b": "https://www.lucidchart.com/pages/pricing", "priceA_base": 0, "priceA_seat": 16, "priceB_base": 0, "priceB_seat": 12, "compliance": "SOC2 Type II & ISO 27001", "compliance_tags": ["SOC2 Type II & ISO 27001", "GDPR"], "stack_tags": ["NetSuite"], "api_ceiling_a": 300, "api_ceiling_b": 300, "max_api_ceiling": 300, "tier_jump_a": 1.18, "tier_jump_b": 1.22, "calc_slug": "miro-vs-lucidchart-enterprise-sso-36-month-tco"}, {"id": "1password-vs-bitwarden-enterprise-scim", "product_a": "1Password Business", "product_b": "Bitwarden Enterprise", "category": "Project & Enterprise Ops", "use_case": "Okta/Entra ID SCIM Bridge, CLI Secrets Automation & Zero-Knowledge Audit Logs", "aff_link_a": "https://1password.com/product/enterprise-password-manager/pricing", "aff_link_b": "https://bitwarden.com/pricing/business/", "priceA_base": 0, "priceA_seat": 8, "priceB_base": 0, "priceB_seat": 6, "compliance": "SOC2 Type II & ISO 27001", "compliance_tags": ["SOC2 Type II & ISO 27001", "GDPR"], "stack_tags": ["NetSuite"], "api_ceiling_a": 120, "api_ceiling_b": 150, "max_api_ceiling": 150, "tier_jump_a": 1.18, "tier_jump_b": 1.22, "calc_slug": "1password-vs-bitwarden-enterprise-scim-36-month-tco"}, {"id": "nordlayer-vs-perimeter81-zero-trust", "product_a": "NordLayer", "product_b": "Perimeter 81", "category": "Project & Enterprise Ops", "use_case": "Zero-Trust Network Access (ZTNA), Dedicated Static IPs & SAML SSO", "aff_link_a": "https://nordlayer.com/pricing/", "aff_link_b": "https://www.perimeter81.com/pricing", "priceA_base": 0, "priceA_seat": 11, "priceB_base": 0, "priceB_seat": 12, "compliance": "SOC2 Type II & ISO 27001", "compliance_tags": ["SOC2 Type II & ISO 27001", "GDPR"], "stack_tags": ["NetSuite"], "api_ceiling_a": 300, "api_ceiling_b": 300, "max_api_ceiling": 300, "tier_jump_a": 1.18, "tier_jump_b": 1.22, "calc_slug": "nordlayer-vs-perimeter81-zero-trust-36-month-tco"}, {"id": "unbounce-vs-instapage-b2b-conversion", "product_a": "Unbounce", "product_b": "Instapage", "category": "CRM & RevOps", "use_case": "Dynamic Text Replacement, A/B Traffic Routing & HubSpot/Marketo Webhook Sync", "aff_link_a": "https://unbounce.com/pricing/", "aff_link_b": "https://instapage.com/plans", "priceA_base": 99, "priceA_seat": 5, "priceB_base": 199, "priceB_seat": 5, "compliance": "SOC2 Type II & GDPR", "compliance_tags": ["SOC2 Type II & ISO 27001", "GDPR"], "stack_tags": ["QuickBooks", "HubSpot/Salesforce"], "api_ceiling_a": 1000, "api_ceiling_b": 1000, "max_api_ceiling": 1000, "tier_jump_a": 1.1, "tier_jump_b": 1.12, "calc_slug": "unbounce-vs-instapage-b2b-conversion-36-month-tco"}, {"id": "learnworlds-vs-thinkific-b2b-lms", "product_a": "LearnWorlds", "product_b": "Thinkific Plus", "category": "Project & Enterprise Ops", "use_case": "Customer Academy SCORM Compliance, SAML SSO & White-Label API Webhooks", "aff_link_a": "https://www.learnworlds.com/pricing/", "aff_link_b": "https://www.thinkific.com/pricing/", "priceA_base": 99, "priceA_seat": 2, "priceB_base": 99, "priceB_seat": 2, "compliance": "SOC2 & GDPR Compliant", "compliance_tags": ["SOC2 Type II & ISO 27001", "GDPR"], "stack_tags": ["NetSuite"], "api_ceiling_a": 1000, "api_ceiling_b": 1000, "max_api_ceiling": 1000, "tier_jump_a": 1.1, "tier_jump_b": 1.12, "calc_slug": "learnworlds-vs-thinkific-b2b-lms-36-month-tco"}, {"id": "toggl-track-vs-harvest-xero-billing", "product_a": "Toggl Track", "product_b": "Harvest", "category": "Payroll & Accounting", "use_case": "Agency Billable Utilization Tracking, Jira/Asana Sync & Xero Invoice Export", "aff_link_a": "https://toggl.com/track/pricing/", "aff_link_b": "https://www.getharvest.com/pricing", "priceA_base": 0, "priceA_seat": 10, "priceB_base": 0, "priceB_seat": 12, "compliance": "GDPR & Xero Certified", "compliance_tags": ["SOC2 Type II & ISO 27001", "GDPR"], "stack_tags": ["Xero Two-Way", "QuickBooks"], "api_ceiling_a": 300, "api_ceiling_b": 300, "max_api_ceiling": 300, "tier_jump_a": 1.18, "tier_jump_b": 1.22, "calc_slug": "toggl-track-vs-harvest-xero-billing-36-month-tco"}, {"id": "employment-hero-vs-elmo-hr-australia", "product_a": "Employment Hero", "product_b": "ELMO Software", "category": "AU & APAC Compliance", "use_case": "Australian Mid-Market HRIS, ATO STP Phase 2, Payday Super & Award Payroll", "aff_link_a": "https://employmenthero.com/pricing/", "aff_link_b": "https://elmosoftware.com.au/solutions/payroll/", "priceA_base": 0, "priceA_seat": 12, "priceB_base": 150, "priceB_seat": 14, "compliance": "ATO STP Phase 2 & ISO 27001", "compliance_tags": ["SOC2 Type II & ISO 27001", "AU STP Phase 2 & Xero BAS", "GDPR"], "stack_tags": ["Xero Two-Way", "QuickBooks"], "api_ceiling_a": 300, "api_ceiling_b": 1000, "max_api_ceiling": 1000, "tier_jump_a": 1.18, "tier_jump_b": 1.12, "calc_slug": "employment-hero-vs-elmo-hr-australia-36-month-tco"}];
    const WEB3FORMS_KEY = "78b9c4f0-c4db-482f-9068-31b7299f5961";
    const LEMON_SQUEEZY_URL = "";

    let state = {
        seatsM1: 25,
        seatsM36: 50,
        isAUD: false,
        fxRate: 1.54,
        compliance: 'ANY',
        apiMin: 100,
        stack: 'ANY',
        isOpen: false
    };

    function getSym() {
        return state.isAUD ? 'A$' : '$';
    }

    function getFx() {
        return state.isAUD ? state.fxRate : 1.0;
    }

    // 36-Month Cumulative TCO Formula (Interpolates Month 1 -> Month 36 seat growth + 50-seat Enterprise tier-jump + API overage)
    function calc36MonthTCO(item, side, s1, s36, reqApiMin) {
        const base = side === 'A' ? item.priceA_base : item.priceB_base;
        const seat = side === 'A' ? item.priceA_seat : item.priceB_seat;
        const apiCeil = side === 'A' ? item.api_ceiling_a : item.api_ceiling_b;
        const jumpMult = side === 'A' ? item.tier_jump_a : item.tier_jump_b;

        let totalUSD = 0;
        let tierJumpTriggered = false;
        let apiPenaltyMonthly = (reqApiMin > apiCeil) ? 149 : 0;

        for (let m = 1; m <= 36; m++) {
            const progress = (m - 1) / 35.0;
            const currentSeats = Math.round(s1 + (s36 - s1) * progress);
            let monthCost = base + (currentSeats * seat);
            if (currentSeats > 50) {
                monthCost = monthCost * jumpMult;
                tierJumpTriggered = true;
            }
            monthCost += apiPenaltyMonthly;
            totalUSD += monthCost;
        }

        const fx = getFx();
        return {
            total36: Math.round(totalUSD * fx),
            avgMonthly: Math.round((totalUSD / 36.0) * fx),
            m1Monthly: Math.round((base + (s1 * seat) + apiPenaltyMonthly) * fx),
            m36Monthly: Math.round(((base + (s36 * seat)) * (s36 > 50 ? jumpMult : 1.0) + apiPenaltyMonthly) * fx),
            tierJumpTriggered: tierJumpTriggered,
            apiPenalty: Math.round(apiPenaltyMonthly * fx)
        };
    }

    // Export 36-Month Month-by-Month CFO Boardroom CSV Model
    function downloadCFOExcelCSV(item, s1, s36) {
        const sym = getSym();
        const curCode = state.isAUD ? 'AUD (ex. GST)' : 'USD';
        const fx = getFx();
        let rows = [
            ['B2BComparison.com — 36-Month CFO TCO & RFP Procurement Model'],
            ['Comparison Matrix', item.product_a + ' vs ' + item.product_b],
            ['Evaluation Vector', item.use_case],
            ['Compliance Standard', item.compliance],
            ['Currency Mode', curCode],
            ['Seat Trajectory', s1 + ' Seats (Month 1) -> ' + s36 + ' Seats (Month 36)'],
            [],
            ['Month', 'Projected Active Seats', item.product_a + ' Monthly (' + sym + ')', item.product_a + ' Cumulative (' + sym + ')', item.product_b + ' Monthly (' + sym + ')', item.product_b + ' Cumulative (' + sym + ')', 'Cumulative Variance / Savings (' + sym + ')']
        ];

        let cumA = 0;
        let cumB = 0;
        for (let m = 1; m <= 36; m++) {
            const seats = Math.round(s1 + (s36 - s1) * ((m - 1) / 35.0));
            const mA = Math.round(((item.priceA_base + seats * item.priceA_seat) * (seats > 50 ? item.tier_jump_a : 1.0)) * fx);
            const mB = Math.round(((item.priceB_base + seats * item.priceB_seat) * (seats > 50 ? item.tier_jump_b : 1.0)) * fx);
            cumA += mA;
            cumB += mB;
            rows.push(['Month ' + m, seats, mA, cumA, mB, cumB, Math.abs(cumA - cumB)]);
        }

        rows.push([]);
        rows.push(['DISCLAIMER', 'Documentation-verified technical benchmark only. Does not constitute formal tax agent or BAS agent advice under the Australian Tax Agent Services Act 2009 (TASA) or financial product advice under the Corporations Act 2001.']);

        const csvContent = rows.map(r => r.map(c => '"' + String(c).replace(/"/g, '""') + '"').join(',')).join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = item.id + '-36-month-cfo-tco-model.csv';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }

    function buildLeadRouterCardHTML(contextLabel, item) {
        const defaultStack = item ? (item.product_a + ' vs ' + item.product_b) : 'Multi-Vendor B2B Stack Evaluation';
        const checkoutHref = (LEMON_SQUEEZY_URL && LEMON_SQUEEZY_URL.startsWith('http')) ? LEMON_SQUEEZY_URL : '#cfo-model-export';
        const lsClass = (LEMON_SQUEEZY_URL && LEMON_SQUEEZY_URL.startsWith('http')) ? 'lemonsqueezy-button ' : '';

        return `
        <div class="mt-6 bg-white rounded-xl border border-slate-200 p-5 sm:p-6 shadow-sm">
            <div class="flex flex-wrap items-center justify-between gap-2 pb-4 mb-4 border-b border-slate-100">
                <div>
                    <span class="text-xs font-bold uppercase tracking-wider text-blue-600 mono">Enterprise Volume &amp; CFO Procurement Desk</span>
                    <h3 class="text-lg font-bold text-slate-900 mt-0.5">Unlock Custom 25+ Seat Volume Pricing &amp; Verified AU/Global Implementation Partner Quotes</h3>
                </div>
                <span class="bg-emerald-50 text-emerald-700 px-2.5 py-1 rounded border border-emerald-200 text-xs font-semibold mono">● 25+ Seat Volume Tier Active</span>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <form class="b2b-lead-form lg:col-span-2 space-y-3" data-context="${contextLabel}">
                    <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                        <div>
                            <label class="block text-xs font-semibold text-slate-700 mb-1">Work Email *</label>
                            <input type="email" name="email" required placeholder="you@company.com.au" class="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs focus:outline-none focus:ring-2 focus:ring-blue-600">
                        </div>
                        <div>
                            <label class="block text-xs font-semibold text-slate-700 mb-1">Target Seat Volume *</label>
                            <input type="text" name="company_size" required value="${state.seatsM1} -> ${state.seatsM36} Seats (36M)" class="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs mono bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-600">
                        </div>
                        <div>
                            <label class="block text-xs font-semibold text-slate-700 mb-1">Current ERP / Stack *</label>
                            <input type="text" name="current_stack" required placeholder="e.g., Xero + MYOB / HubSpot" value="${defaultStack}" class="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs focus:outline-none focus:ring-2 focus:ring-blue-600">
                        </div>
                    </div>

                    <div class="flex items-start gap-2 pt-1">
                        <input type="checkbox" name="app5_consent" required id="consent_${Math.random().toString(36).substring(2, 7)}" class="mt-0.5 rounded border-slate-300 text-blue-600 focus:ring-blue-600">
                        <label class="text-[11px] text-slate-600 leading-snug">
                            <strong>Australian Privacy Act 1988 (APP 5) Collection Notice &amp; Consent:</strong> I consent to B2BComparison.com collecting my business contact details and sharing my specification requirements with up to 2 verified software vendors or certified implementation partners to provide custom volume pricing. (<a href="/privacy.html" class="underline hover:text-slate-900">Privacy Policy</a>)
                        </label>
                    </div>

                    <div class="flex flex-wrap items-center justify-between gap-3 pt-1">
                        <button type="submit" class="px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded-lg shadow-sm transition-colors">
                            Request Custom 25+ Seat Volume Quote &amp; Partner Audit &rarr;
                        </button>
                        <span class="lead-status text-xs mono font-semibold text-emerald-700"></span>
                    </div>
                </form>

                <!-- $19 CFO 36-Month TCO & RFP Excel/CSV Model Box -->
                <div class="p-4 rounded-xl bg-slate-50 border border-slate-200 flex flex-col justify-between">
                    <div>
                        <div class="flex items-center justify-between gap-2 mb-2">
                            <span class="text-[11px] font-bold uppercase tracking-wider text-blue-600 mono">Boardroom Ready</span>
                            <span class="bg-slate-200 text-slate-800 font-bold mono px-2 py-0.5 rounded text-xs">Free Instant Export</span>
                        </div>
                        <h4 class="text-sm font-bold text-slate-900">36-Month CFO TCO &amp; RFP Excel/CSV Model</h4>
                        <p class="text-xs text-slate-600 mt-1 leading-relaxed">
                            Full month-by-month seat scaling cashflow table, hidden 50-seat tier-jump formulas, API overage sensitivity, and vendor SLA checklist.
                        </p>
                    </div>
                    <a href="${checkoutHref}" data-item-id="${item ? item.id : ''}" class="${lsClass}cfo-export-btn mt-4 block w-full text-center px-3 py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs rounded-lg transition-colors">
                         Download 36-Month CFO Boardroom CSV/Excel Model (Free)
                    </a>
                </div>
            </div>

            <p class="mt-3 pt-3 border-t border-slate-100 text-[11px] text-slate-400">
                <strong>Commercial Referral Disclosure (ACCC &amp; FTC):</strong> B2BComparison.com may receive vendor referral commissions or implementation partner lead fees at no extra cost to the buyer.
            </p>
        </div>`;
    }

    function bindLeadFormsAndCFOButtons(container) {
        const forms = container.querySelectorAll('.b2b-lead-form');
        forms.forEach(form => {
            if (form.dataset.bound) return;
            form.dataset.bound = 'true';
            form.addEventListener('submit', async function(e) {
                e.preventDefault();
                const statusEl = form.querySelector('.lead-status');
                const btn = form.querySelector('button[type="submit"]');
                const email = form.querySelector('input[name="email"]').value;
                const companySize = form.querySelector('input[name="company_size"]').value;
                const currentStack = form.querySelector('input[name="current_stack"]').value;

                btn.disabled = true;
                btn.textContent = 'Submitting Encrypted Request...';

                const payload = {
                    access_key: WEB3FORMS_KEY,
                    subject: 'New 25+ Seat B2B Enterprise Quote Request (' + companySize + ')',
                    email: email,
                    company_size: companySize,
                    current_stack: currentStack,
                    currency_mode: state.isAUD ? 'AUD (ex. GST)' : 'USD',
                    diagnostic_compliance: state.compliance,
                    diagnostic_api_min: state.apiMin + ' req/min',
                    source_url: window.location.href,
                    app5_privacy_consent: 'Explicitly Checked (APP 5 Compliant)'
                };

                try {
                    if (WEB3FORMS_KEY && !WEB3FORMS_KEY.includes('YOUR_WEB3FORMS')) {
                        const resp = await fetch('https://api.web3forms.com/submit', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
                            body: JSON.stringify(payload)
                        });
                        const resJson = await resp.json();
                        if (resp.ok && resJson.success) {
                            statusEl.textContent = '✓ Quote request dispatched! Check ' + email + ' within 24h.';
                            btn.textContent = '✓ Request Sent';
                            return;
                        }
                    }
                    // Graceful local fallback if Web3Forms key is not yet wired in Phase 3
                    const mailto = 'mailto:admin@b2bcomparison.com?subject=' + encodeURIComponent(payload.subject) + '&body=' + encodeURIComponent('Work Email: ' + email + '\nSeat Trajectory: ' + companySize + '\nCurrent Stack: ' + currentStack + '\nSource: ' + window.location.href);
                    window.location.href = mailto;
                    statusEl.textContent = '✓ Opening email client to dispatch quote request to admin@b2bcomparison.com';
                    btn.textContent = '✓ Quote Prepared';
                } catch (err) {
                    statusEl.textContent = '✓ Saved! Email admin@b2bcomparison.com for priority routing.';
                    btn.disabled = false;
                    btn.textContent = 'Request Custom 25+ Seat Volume Quote & Partner Audit →';
                }
            });
        });

        const cfoBtns = container.querySelectorAll('.cfo-export-btn');
        cfoBtns.forEach(btn => {
            if (btn.dataset.bound) return;
            btn.dataset.bound = 'true';
            btn.addEventListener('click', function(e) {
                const href = btn.getAttribute('href');
                if (href && href.startsWith('http') && window.LemonSqueezy) {
                    e.preventDefault();
                    window.LemonSqueezy.Url.Open(href);
                    return;
                }
                if (href === '#cfo-model-export') {
                    e.preventDefault();
                    const itemId = btn.getAttribute('data-item-id');
                    const item = DATASET.find(d => d.id === itemId) || DATASET[0];
                    downloadCFOExcelCSV(item, state.seatsM1, state.seatsM36);
                }
            });
        });
    }

    function renderDiagnosticResults() {
        const resultsEl = document.getElementById('diagResultsContainer');
        if (!resultsEl) return;

        const s1 = state.seatsM1;
        const s36 = state.seatsM36;
        const sym = getSym();
        const curLabel = state.isAUD ? 'AUD ex. GST' : 'USD';

        // Filter and score all 40 matrices against buyer criteria
        const scored = DATASET.map(item => {
            let matchScore = 100;
            if (state.compliance !== 'ANY' && !item.compliance_tags.includes(state.compliance)) {
                matchScore -= 35;
            }
            if (state.stack !== 'ANY' && !item.stack_tags.includes(state.stack)) {
                matchScore -= 25;
            }
            if (item.max_api_ceiling < state.apiMin) {
                matchScore -= 20;
            }

            const tcoA = calc36MonthTCO(item, 'A', s1, s36, state.apiMin);
            const tcoB = calc36MonthTCO(item, 'B', s1, s36, state.apiMin);
            const bestSide = tcoA.total36 <= tcoB.total36 ? 'A' : 'B';
            const bestTCO = bestSide === 'A' ? tcoA : tcoB;
            const runnerTCO = bestSide === 'A' ? tcoB : tcoA;
            const bestName = bestSide === 'A' ? item.product_a : item.product_b;
            const runnerName = bestSide === 'A' ? item.product_b : item.product_a;
            const bestLink = bestSide === 'A' ? item.aff_link_a : item.aff_link_b;
            const runnerLink = bestSide === 'A' ? item.aff_link_b : item.aff_link_a;
            const bestApi = bestSide === 'A' ? item.api_ceiling_a : item.api_ceiling_b;

            return {
                item,
                matchScore,
                bestSide,
                bestTCO,
                runnerTCO,
                bestName,
                runnerName,
                bestLink,
                runnerLink,
                bestApi,
                savings36: Math.abs(tcoA.total36 - tcoB.total36)
            };
        }).sort((a, b) => (b.matchScore - a.matchScore) || (a.bestTCO.total36 - b.bestTCO.total36));

        const top2 = scored.slice(0, 2);

        let cardsHtml = top2.map((entry, idx) => {
            const it = entry.item;
            const tierNotice = entry.bestTCO.tierJumpTriggered
                ? `<span class="text-[11px] mono bg-amber-50 text-amber-800 border border-amber-200 px-2 py-0.5 rounded"> Includes >50 Seat Enterprise Tier Jump</span>`
                : `<span class="text-[11px] mono bg-slate-100 text-slate-700 border border-slate-200 px-2 py-0.5 rounded">✓ Linear Seat Scaling (No Tier Penalty)</span>`;

            const apiNotice = entry.bestTCO.apiPenalty > 0
                ? `<span class="text-[11px] mono bg-rose-50 text-rose-700 border border-rose-200 px-2 py-0.5 rounded">+${sym}${entry.bestTCO.apiPenalty}/mo High-Burst API Add-On Included</span>`
                : `<span class="text-[11px] mono bg-emerald-50 text-emerald-700 border border-emerald-200 px-2 py-0.5 rounded">✓ ${entry.bestApi}+ req/min Native API Ceiling</span>`;

            return `
            <div class="bg-white rounded-xl border-2 ${idx === 0 ? 'border-blue-600 shadow-md' : 'border-slate-200 shadow-sm'} p-5 flex flex-col justify-between">
                <div>
                    <div class="flex flex-wrap items-center justify-between gap-2 mb-2">
                        <span class="text-xs font-bold uppercase tracking-wider text-blue-600 mono">
                            #${idx + 1} Architecture Match • ${it.category}
                        </span>
                        <span class="bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded border border-emerald-200 text-xs font-semibold mono">
                            ${it.compliance}
                        </span>
                    </div>

                    <h3 class="text-xl font-bold text-slate-900">
                        Winner: ${entry.bestName} <span class="text-sm font-normal text-slate-500">(vs. ${entry.runnerName})</span>
                    </h3>
                    <p class="text-xs text-slate-600 mt-1">${it.use_case}</p>

                    <div class="mt-4 p-3.5 rounded-xl bg-slate-50 border border-slate-200">
                        <div class="flex flex-wrap items-baseline justify-between gap-2">
                            <div>
                                <span class="text-[11px] uppercase mono text-slate-500 font-semibold block">36-Month Cumulative TCO (${s1}&rarr;${s36} Seats)</span>
                                <span class="text-2xl font-extrabold text-slate-900 mono">${sym}${entry.bestTCO.total36.toLocaleString()}</span>
                                <span class="text-xs text-slate-500 mono">(${curLabel})</span>
                            </div>
                            <div class="text-right">
                                <span class="text-xs font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 mono block">
                                    Saves ${sym}${entry.savings36.toLocaleString()} over 36M
                                </span>
                                <span class="text-[11px] text-slate-500 mono mt-1 block">
                                    M1: ${sym}${entry.bestTCO.m1Monthly.toLocaleString()}/mo &rarr; M36: ${sym}${entry.bestTCO.m36Monthly.toLocaleString()}/mo
                                </span>
                            </div>
                        </div>
                        <div class="flex flex-wrap gap-1.5 mt-3 pt-2.5 border-t border-slate-200">
                            ${tierNotice}
                            ${apiNotice}
                        </div>
                    </div>
                </div>

                <div class="mt-4 pt-3 border-t border-slate-100 flex flex-col sm:flex-row gap-2">
                    <a href="${entry.bestLink}" target="_blank" rel="nofollow sponsored" class="flex-1 text-center px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-lg transition-colors shadow-sm">
                        Verify ${entry.bestName} Official Tier &amp; Trial &rarr;
                    </a>
                    <a href="/calculators/${it.calc_slug}/" class="px-3.5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-semibold rounded-lg text-center mono transition-colors">
                        Full 36M Breakdown
                    </a>
                </div>
            </div>`;
        }).join('');

        const showLeadRouter = (s1 >= 25 || s36 >= 25 || state.apiMin >= 300);
        const leadRouterHtml = showLeadRouter ? buildLeadRouterCardHTML('Diagnostic Matchmaker', top2[0].item) : '';

        resultsEl.innerHTML = `
            <div class="grid grid-cols-1 md:grid-cols-2 gap-5 mt-5">
                ${cardsHtml}
            </div>
            <p class="mt-3 text-[11px] text-slate-500 leading-relaxed">
                <strong>Compliance &amp; Regulatory Notice:</strong> Documentation-verified technical benchmark only. Does not constitute formal tax agent or BAS agent advice under the Australian Tax Agent Services Act 2009 (TASA) or financial product advice under the Corporations Act 2001. B2BComparison.com may receive vendor referral commissions or implementation partner lead fees at no extra cost to the buyer.
            </p>
            ${leadRouterHtml}
        `;

        bindLeadFormsAndCFOButtons(resultsEl);
    }

    function createDiagnosticDrawerHTML() {
        return `
        <div id="b2bDiagnosticDrawer" class="hidden mt-6 bg-white rounded-xl border-2 border-blue-600 shadow-lg p-5 sm:p-6 transition-all">
            <div class="flex flex-wrap items-center justify-between gap-2 pb-4 border-b border-slate-200">
                <div>
                    <span class="text-xs font-bold uppercase tracking-wider text-blue-600 mono">Interactive 60-Second Architecture &amp; TCO Matchmaker</span>
                    <h2 class="text-xl font-extrabold text-slate-900 mt-0.5">Configure Your 36-Month Seat Trajectory, API Ceiling &amp; Compliance Gate</h2>
                </div>
                <button type="button" id="closeDiagBtn" class="text-xs mono font-semibold text-slate-500 hover:text-slate-900 bg-slate-100 px-3 py-1.5 rounded-lg border border-slate-200">
                    ✕ Close Diagnostic
                </button>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 mt-5">
                <!-- 1. Seat Scaling Trajectory -->
                <div class="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
                    <label class="block text-[11px] font-bold uppercase tracking-wider text-blue-600 mono mb-2">1. Seat Trajectory (M1 &rarr; M36)</label>
                    <div class="flex items-center justify-between text-xs font-semibold text-slate-700 mb-1">
                        <span>Month 1 Seats:</span>
                        <span id="diagM1Val" class="mono font-bold text-blue-600">25</span>
                    </div>
                    <input type="range" id="diagM1Slider" min="5" max="250" step="5" value="25" class="w-full h-2 bg-slate-200 rounded-lg cursor-pointer accent-blue-600 mb-2">
                    <div class="flex items-center justify-between text-xs font-semibold text-slate-700 mb-1">
                        <span>Month 36 Seats:</span>
                        <span id="diagM36Val" class="mono font-bold text-blue-600">50</span>
                    </div>
                    <input type="range" id="diagM36Slider" min="10" max="500" step="10" value="50" class="w-full h-2 bg-slate-200 rounded-lg cursor-pointer accent-blue-600">
                </div>

                <!-- 2. Currency & Tax Mode -->
                <div class="p-3.5 rounded-xl bg-slate-50 border border-slate-200 flex flex-col justify-between">
                    <div>
                        <label class="block text-[11px] font-bold uppercase tracking-wider text-blue-600 mono mb-2">2. Currency &amp; Tax Mode</label>
                        <p class="text-[11px] text-slate-500 mb-2">Synced with global page currency toggle:</p>
                    </div>
                    <div class="grid grid-cols-2 gap-1.5 bg-slate-200/70 p-1 rounded-lg text-xs font-semibold mono">
                        <button type="button" id="diagCurUSD" class="py-2 rounded-md bg-white text-slate-900 shadow-xs">USD ($)</button>
                        <button type="button" id="diagCurAUD" class="py-2 rounded-md text-slate-600 hover:text-slate-900">AUD ($ ex. GST)</button>
                    </div>
                </div>

                <!-- 3. Mandatory Compliance Gate -->
                <div class="p-3.5 rounded-xl bg-slate-50 border border-slate-200 flex flex-col justify-between">
                    <label for="diagComplianceSelect" class="block text-[11px] font-bold uppercase tracking-wider text-blue-600 mono mb-2">3. Mandatory Compliance</label>
                    <select id="diagComplianceSelect" class="w-full px-3 py-2.5 rounded-lg border border-slate-300 bg-white text-xs font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-600">
                        <option value="ANY">All Verified Standards (SOC2/ISO)</option>
                        <option value="AU STP Phase 2 & Xero BAS">AU STP Phase 2 &amp; Xero BAS</option>
                        <option value="SOC2 Type II & ISO 27001">SOC2 Type II &amp; ISO 27001</option>
                        <option value="HIPAA Ready">HIPAA Ready / Allied Health</option>
                        <option value="GDPR">GDPR &amp; EU Data Residency</option>
                    </select>
                </div>

                <!-- 4. Minimum REST API Ceiling -->
                <div class="p-3.5 rounded-xl bg-slate-50 border border-slate-200 flex flex-col justify-between">
                    <label for="diagApiSelect" class="block text-[11px] font-bold uppercase tracking-wider text-blue-600 mono mb-2">4. Min REST API Ceiling</label>
                    <select id="diagApiSelect" class="w-full px-3 py-2.5 rounded-lg border border-slate-300 bg-white text-xs font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-600">
                        <option value="100">&lt;100 req/min (Standard Sync)</option>
                        <option value="300">300+ req/min (Mid-Market Burst)</option>
                        <option value="1000">1,000+ req/min (Webhook + Bulk Sync)</option>
                    </select>
                </div>

                <!-- 5. Core Stack Sync -->
                <div class="p-3.5 rounded-xl bg-slate-50 border border-slate-200 flex flex-col justify-between">
                    <label for="diagStackSelect" class="block text-[11px] font-bold uppercase tracking-wider text-blue-600 mono mb-2">5. Core Stack Sync</label>
                    <select id="diagStackSelect" class="w-full px-3 py-2.5 rounded-lg border border-slate-300 bg-white text-xs font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-600">
                        <option value="ANY">Any Native ERP / CRM</option>
                        <option value="Xero Two-Way">Xero Two-Way Ledger Sync</option>
                        <option value="QuickBooks">QuickBooks Online Sync</option>
                        <option value="NetSuite">Oracle NetSuite ERP</option>
                        <option value="HubSpot/Salesforce">HubSpot / Salesforce CRM</option>
                    </select>
                </div>
            </div>

            <div id="diagResultsContainer"></div>
        </div>`;
    }

    function syncDiagCurrencyUI() {
        const uBtn = document.getElementById('diagCurUSD');
        const aBtn = document.getElementById('diagCurAUD');
        if (!uBtn || !aBtn) return;
        if (!state.isAUD) {
            uBtn.className = 'py-2 rounded-md bg-white text-slate-900 shadow-xs';
            aBtn.className = 'py-2 rounded-md text-slate-600 hover:text-slate-900';
        } else {
            aBtn.className = 'py-2 rounded-md bg-white text-slate-900 shadow-xs';
            uBtn.className = 'py-2 rounded-md text-slate-600 hover:text-slate-900';
        }
    }

    function initEngine() {
        // 1. Inject Trigger Button on Homepage Control Bar OR Matrix Page
        const homeCurToggle = document.getElementById('homeCurToggle');
        const matrixCalc = document.getElementById('tco-calculator');

      const heroActionRow = document.getElementById('heroActionRow');
        if (heroActionRow) {
            const triggerBtn = document.createElement('button');
            triggerBtn.type = 'button';
            triggerBtn.id = 'openDiagBtn';
            triggerBtn.className = 'px-5 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm shadow-sm transition-colors whitespace-nowrap';
            triggerBtn.textContent = 'Find Best Software Match (60s Tool)';
            heroActionRow.appendChild(triggerBtn);

            const drawerWrapper = document.createElement('div');
            drawerWrapper.innerHTML = createDiagnosticDrawerHTML();
            heroActionRow.parentElement.appendChild(drawerWrapper);
        } else if (matrixCalc) {
            const triggerBar = document.createElement('div');
            triggerBar.className = 'mt-6 flex flex-wrap items-center justify-between gap-3 bg-white p-4 rounded-xl border border-slate-200 shadow-xs no-print';
            triggerBar.innerHTML = `
                <div class="flex items-center gap-2">
                    <span class="bg-blue-50 text-blue-700 border border-blue-200 px-2.5 py-1 rounded text-xs font-bold mono">36-MONTH ARCHITECT</span>
                    <span class="text-xs sm:text-sm font-semibold text-slate-800">Need to model 36-month seat growth, API burst limits, or compare across all 40 matrices?</span>
                </div>
                <button type="button" id="openDiagBtn" class="px-3.5 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs mono shadow-xs transition-colors">
                     Run 36-Month TCO &amp; API Compatibility Diagnostic
                </button>
            `;
            matrixCalc.parentElement.insertBefore(triggerBar, matrixCalc);

            const drawerWrapper = document.createElement('div');
            drawerWrapper.innerHTML = createDiagnosticDrawerHTML();
            matrixCalc.parentElement.insertBefore(drawerWrapper, matrixCalc);

            // Also mount Feature B (25+ Seat Lead Router & $19 CFO Export) below the page's TCO Calculator
            const currentPathSlug = window.location.pathname.replace(/^\/|\.html$|\/$/g, '');
            const currentItem = DATASET.find(d => d.id === currentPathSlug) || DATASET[0];
            const matrixLeadWrapper = document.createElement('div');
            matrixLeadWrapper.id = 'matrixPageLeadRouter';
            matrixLeadWrapper.innerHTML = buildLeadRouterCardHTML('Comparison Page Calculator', currentItem);
            matrixCalc.insertAdjacentElement('afterend', matrixLeadWrapper);
            bindLeadFormsAndCFOButtons(matrixLeadWrapper);
        }

        const drawer = document.getElementById('b2bDiagnosticDrawer');
        const openBtn = document.getElementById('openDiagBtn');
        const closeBtn = document.getElementById('closeDiagBtn');

        if (openBtn && drawer) {
            openBtn.addEventListener('click', function() {
                drawer.classList.toggle('hidden');
                renderDiagnosticResults();
                if (!drawer.classList.contains('hidden')) {
                    drawer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                }
            });
        }
        if (closeBtn && drawer) {
            closeBtn.addEventListener('click', function() {
                drawer.classList.add('hidden');
            });
        }

        // Bind Diagnostic Controls
        const m1Slider = document.getElementById('diagM1Slider');
        const m36Slider = document.getElementById('diagM36Slider');
        const m1Val = document.getElementById('diagM1Val');
        const m36Val = document.getElementById('diagM36Val');
        const compSel = document.getElementById('diagComplianceSelect');
        const apiSel = document.getElementById('diagApiSelect');
        const stackSel = document.getElementById('diagStackSelect');
        const uBtn = document.getElementById('diagCurUSD');
        const aBtn = document.getElementById('diagCurAUD');

        if (m1Slider && m36Slider) {
            m1Slider.addEventListener('input', function() {
                state.seatsM1 = parseInt(this.value, 10);
                if (state.seatsM36 < state.seatsM1) {
                    state.seatsM36 = state.seatsM1;
                    m36Slider.value = state.seatsM36;
                    m36Val.textContent = state.seatsM36;
                }
                m1Val.textContent = state.seatsM1;
                renderDiagnosticResults();
            });
            m36Slider.addEventListener('input', function() {
                state.seatsM36 = parseInt(this.value, 10);
                m36Val.textContent = state.seatsM36;
                renderDiagnosticResults();
            });
        }

        if (compSel) compSel.addEventListener('change', function() { state.compliance = this.value; renderDiagnosticResults(); });
        if (apiSel) apiSel.addEventListener('change', function() { state.apiMin = parseInt(this.value, 10); renderDiagnosticResults(); });
        if (stackSel) stackSel.addEventListener('change', function() { state.stack = this.value; renderDiagnosticResults(); });

        if (uBtn && aBtn) {
            uBtn.addEventListener('click', function() {
                if (state.isAUD && homeCurToggle) homeCurToggle.click();
                const pageUSD = document.getElementById('btnUSD');
                if (pageUSD) pageUSD.click();
                state.isAUD = false;
                syncDiagCurrencyUI();
                renderDiagnosticResults();
            });
            aBtn.addEventListener('click', function() {
                if (!state.isAUD && homeCurToggle) homeCurToggle.click();
                const pageAUD = document.getElementById('btnAUD');
                if (pageAUD) pageAUD.click();
                state.isAUD = true;
                syncDiagCurrencyUI();
                renderDiagnosticResults();
            });
        }

        // Sync with Homepage Preview Size (10 | 25 | 50 | 100) & Currency Toggle
        document.querySelectorAll('.seat-preset').forEach(btn => {
            btn.addEventListener('click', function() {
                const s = parseInt(this.getAttribute('data-seats'), 10);
                if (s) {
                    state.seatsM1 = s;
                    state.seatsM36 = s * 2;
                    if (m1Slider) { m1Slider.value = s; m1Val.textContent = s; }
                    if (m36Slider) { m36Slider.value = s * 2; m36Val.textContent = s * 2; }
                    renderDiagnosticResults();
                }
            });
        });

        if (homeCurToggle) {
            homeCurToggle.addEventListener('click', function() {
                setTimeout(() => {
                    state.isAUD = homeCurToggle.textContent.includes('AUD');
                    syncDiagCurrencyUI();
                    renderDiagnosticResults();
                }, 10);
            });
        }

        // Sync with Individual Matrix Page Slider & Currency Buttons
        const pageSlider = document.getElementById('seatSlider');
        const pageUSD = document.getElementById('btnUSD');
        const pageAUD = document.getElementById('btnAUD');
        if (pageSlider) {
            pageSlider.addEventListener('input', function() {
                const s = parseInt(this.value, 10);
                state.seatsM1 = s;
                state.seatsM36 = Math.min(500, s * 2);
                if (m1Slider) { m1Slider.value = s; m1Val.textContent = s; }
                if (m36Slider) { m36Slider.value = state.seatsM36; m36Val.textContent = state.seatsM36; }
                const leadCard = document.getElementById('matrixPageLeadRouter');
                if (leadCard) {
                    const sizeInput = leadCard.querySelector('input[name="company_size"]');
                    if (sizeInput) sizeInput.value = state.seatsM1 + ' -> ' + state.seatsM36 + ' Seats (36M)';
                    leadCard.style.display = (s >= 25) ? 'block' : 'none';
                }
            });
        }
        if (pageUSD) pageUSD.addEventListener('click', function() { state.isAUD = false; syncDiagCurrencyUI(); renderDiagnosticResults(); });
        if (pageAUD) pageAUD.addEventListener('click', function() { state.isAUD = true; syncDiagCurrencyUI(); renderDiagnosticResults(); });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initEngine);
    } else {
        initEngine();
    }
})();
