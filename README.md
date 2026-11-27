# Ross Video — AI-assisted engineering activity assessment (public site)

This repository publishes a **browser-only, static copy of the approved MVP website** using GitHub Pages. The original React/Vite application, KNIME workflow, report documents and development history remain in the **private** repository `Mistu98/ross-ai-assessment-mvp`.

## MVP project status - updated 27 November 2026

**Status: Finalized for capstone demonstration and handover.** The client has reviewed the information presented in the MVP and expressed satisfaction with it. This repository publishes the static demonstration; the editable application source and detailed technical documentation remain in the private source repository.

This completion status does **not** imply production readiness, deployment across Ross engineering teams, independently validated rubric results, a shared assessment database, live KNIME updates, or approval to expose confidential evidence. Activity assessments remain human-led, and any future deployment or integration requires separate review.

The date above is the **GitHub status update date**; research content and implementation identifiers retain their separate source provenance.

## Site

Once deployment succeeds, the expected URL is:

https://mistu98.github.io/ross-assessment-mvp-site/

## How this deployment works

The GitHub Actions workflow mirrors only the public, already-built site from the verified Netlify Deploy Preview for pull request #10:

https://deploy-preview-10--timely-bunny-9be542.netlify.app/

It saves the Vite index, required JavaScript/CSS assets, and the versioned `data/concepts.json` needed by the browser. The original private repository, original screenshots, original reports and KNIME project are **not** downloaded or copied. The mirror script refuses to deploy if the 15-concept JSON source is not tagged `report-2026-11-22-provisional`.

The build adjusts asset links and the concept-data path for the GitHub Pages subdirectory. The website itself is static, and no Netlify hosting is needed to *serve* the deployed site once GitHub Pages is live. A **new** website refresh from that preview does require the preview to remain publicly accessible.

## GitHub Pages setup

On **Settings → Pages**, select **GitHub Actions** under **Build and deployment → Source**. See **Actions → Publish public MVP website** for the deployment outcome.

The first run attempts to enable Pages automatically. If GitHub rejects that change, select GitHub Actions manually in the Pages settings, then re-run the workflow from the Actions tab.

## Privacy and limitations

- **Public website**: all browser-served JavaScript, HTML, CSS, and concept data are publicly retrievable. Confirm Ross permission to distribute the research-derived content.
- **Local-only changes**: activity edits, uploaded attachments, and assessment decisions stay in each user's own browser. This is not multi-user shared storage or an approval backend.
- **Qualitative method**: assessments are research demonstrations, not validated safety/quality scores or automated organizational authorization.
- **No live KNIME integration**: literature exports and method changes are manually reviewed and versioned, not automatically recomputed on GitHub Pages.
- **No automatic source sync**: the static mirror is based on a particular deploy preview. Changes to the private MVP must be reviewed and deliberately republished.
