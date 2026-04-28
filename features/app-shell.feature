Feature: App shell
  As a user
  I want the app shell to load reliably
  So that I can start workflows

  @smoke
  Scenario: App opens with expected initial state
    Given the media downloader app is open
    Then the title bar shows the app name and version
    And the download button is disabled until a URL is entered
