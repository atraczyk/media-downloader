Feature: Main app flows
  As a user
  I want the desktop UI to support core download workflows
  So that I can validate, configure, and complete downloads

  @smoke
  Scenario: App opens with expected initial state
    Given the media downloader app is open
    Then the title bar shows the app name and version
    And the download button is disabled until a URL is entered

  Scenario: URL validation success shows title and allows download
    Given the media downloader app is open
    And validation response for "https://example.com/ok" is valid with title "Demo Video"
    When I enter URL "https://example.com/ok"
    Then URL status contains "Demo Video"
    And the download button is enabled

  Scenario: URL validation failure shows an error
    Given the media downloader app is open
    And validation response for "https://example.com/bad" is invalid with error "Video unavailable"
    When I enter URL "https://example.com/bad"
    Then URL status contains "Video unavailable"

  Scenario: Format selection updates quality options
    Given the media downloader app is open
    When I select video format
    Then the quality options are "Best,1080p,720p,480p,360p"
    When I select audio format
    Then the quality options are "128 kbps,192 kbps,256 kbps,320 kbps"

  Scenario: Browse destination updates the destination input
    Given the media downloader app is open
    And browse folder returns "C:\Downloads\Media"
    When I click Browse for destination
    Then destination is "C:\Downloads\Media"

  Scenario: Start download sends selected options in the request
    Given the media downloader app is open
    And validation response for "https://example.com/video" is valid with title "Payload Video"
    And start download succeeds
    When I enter URL "https://example.com/video"
    And I select video format
    And I select quality "720p"
    And I enable transcript download
    And I set destination to "downloads\custom"
    And I start the download
    Then last start request url is "https://example.com/video"
    And last start request destination is "downloads\custom"
    And last start request downloadType is "video"
    And last start request videoQuality is "720p"
    And last start request transcriptEnabled is true

  Scenario: Progress, completion, and Show in folder are wired
    Given the media downloader app is open
    And validation response for "https://example.com/audio" is valid with title "Audio File"
    And start download succeeds
    When I enter URL "https://example.com/audio"
    And I start the download
    And download reports status "downloading" progress 0.5 message "Downloading chunk"
    Then progress message contains "Downloading chunk"
    When download completes successfully with file "C:\Downloads\Audio File.mp3"
    Then Show in folder action is available
    When I click Show in folder
    Then shell show item is called with "C:\Downloads\Audio File.mp3"

  Scenario: Transcript panel can be shown when transcript text arrives
    Given the media downloader app is open
    When transcript text arrives "Hello transcript"
    Then transcript section is visible
    When I click transcript toggle
    Then transcript text contains "Hello transcript"

  Scenario: Active download can be canceled
    Given the media downloader app is open
    And validation response for "https://example.com/cancel" is valid with title "Cancelable"
    And start download succeeds
    When I enter URL "https://example.com/cancel"
    And I start the download
    Then cancel button is shown
    When I cancel the download
    Then cancel download was requested 1 time
