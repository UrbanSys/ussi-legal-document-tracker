------------------------------------------------------------
-- 1. Lookup tables
------------------------------------------------------------

CREATE TABLE EncumbranceAction (
    Id          INT IDENTITY(1,1) PRIMARY KEY,
    Code        NVARCHAR(50) NOT NULL UNIQUE,  
    Label       NVARCHAR(200) NOT NULL,         -- e.g. 'Discharge'
    Description NVARCHAR(500) NULL
); 

CREATE TABLE EncumbranceStatus (
    Id          INT IDENTITY(1,1) PRIMARY KEY,
    Code        NVARCHAR(50) NOT NULL UNIQUE,   
    Label       NVARCHAR(200) NOT NULL,
    Description NVARCHAR(500) NULL
); 

CREATE TABLE DocumentTaskStatus (
    Id          INT IDENTITY(1,1) PRIMARY KEY,
    Code        NVARCHAR(50) NOT NULL UNIQUE,  -- code = NULL, PREPARED, COMPLETE,
    Label       NVARCHAR(200) NOT NULL,
); 

CREATE TABLE DocumentCategory (
    Id      INT IDENTITY(1,1) PRIMARY KEY,
    Code    NVARCHAR(50) NOT NULL UNIQUE,  -- e.g. 'SUBDIVISION', 'URW', 'NEW_AGREEMENT'
    Name    NVARCHAR(200) NOT NULL
);

CREATE TABLE LegalDocumentTemplate (
    Id            INT IDENTITY(1,1) PRIMARY KEY,
    FilePath      NVARCHAR(500) NOT NULL,
    DocumentType  NVARCHAR(100) NOT NULL,   -- e.g. 'URW_AGREEMENT', 'DISCHARGE', 'CONSENT'
    Municipality  NVARCHAR(200) NULL, --e.g. 'City of Calgary', 'City of Airdrie' 'City of Chestmere', 'Strathcona County'
    Version       NVARCHAR(50) NULL
);

------------------------------------------------------------
-- 2. People / Projects / Title
------------------------------------------------------------

CREATE TABLE SurveyorALS (
    Id          INT IDENTITY(1,1) PRIMARY KEY,
    Name        NVARCHAR(200) NOT NULL,
    FtpNumber   NVARCHAR(50) NULL,
    City        NVARCHAR(200) NULL
    -- add other information later if needed
);

CREATE TABLE Project (
    Id            INT IDENTITY(1,1) PRIMARY KEY,
    ProjNum       NVARCHAR(100) NOT NULL,
    Name          NVARCHAR(300) NOT NULL,
    SurveyorId    INT NULL,
    Municipality  NVARCHAR(200) NULL,
    CONSTRAINT FK_Project_Surveyor
        FOREIGN KEY (SurveyorId) REFERENCES SurveyorALS(Id)
);

CREATE TABLE TitleDocument (
    Id           INT IDENTITY(1,1) PRIMARY KEY,
    ProjectId    INT NOT NULL,
    FilePath     NVARCHAR(500) NOT NULL,
    UploadedBy   NVARCHAR(200) NULL,
    UploadedAt   DATETIME2(0) NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT FK_TitleDocument_Project
        FOREIGN KEY (ProjectId) REFERENCES Project(Id)
        ON DELETE CASCADE
);

------------------------------------------------------------
-- 3. LegalDocument (minimal for now, to support FK from Encumbrance) 
-- not sure if we want to store the completed documents in teh database or just file path references
-- filepaths might not stay the same if archived - might not need this table. 
------------------------------------------------------------

CREATE TABLE LegalDocument (
    Id               INT IDENTITY(1,1) PRIMARY KEY,
    ProjectId        INT NOT NULL,
    FilePath         NVARCHAR(500) NOT NULL,
    DocumentType     NVARCHAR(100) NULL,       -- could align with template type
    RegisteredNumber NVARCHAR(100) NULL,
    RegisteredDate   DATE NULL,
    Notes            NVARCHAR(MAX) NULL,
    CONSTRAINT FK_LegalDocument_Project
        FOREIGN KEY (ProjectId) REFERENCES Project(Id)
);

------------------------------------------------------------
-- 4. Encumbrances (Existing Encumbrances on Title table)
------------------------------------------------------------

CREATE TABLE EncumbranceRow (
    Id                INT IDENTITY(1,1) PRIMARY KEY,
    TitleDocumentId   INT NOT NULL,
    ItemNo            INT NOT NULL,
    DocumentNumber    NVARCHAR(100) NULL,
    EncumbranceDate   DATE NULL,
    Description       NVARCHAR(MAX) NULL,
    Signatories       NVARCHAR(500) NULL,
    ActionId          INT NULL,          -- FK → EncumbranceAction
    StatusId          INT NULL,          -- FK → EncumbranceStatus
    CirculationNotes  NVARCHAR(MAX) NULL,
    LegalDocumentId   INT NULL,          -- FK → LegalDocument (once created) - might remove?
    CONSTRAINT FK_EncumbranceRow_TitleDocument
        FOREIGN KEY (TitleDocumentId) REFERENCES TitleDocument(Id)
        ON DELETE CASCADE,
    CONSTRAINT FK_EncumbranceRow_Action
        FOREIGN KEY (ActionId) REFERENCES EncumbranceAction(Id),
    CONSTRAINT FK_EncumbranceRow_Status
        FOREIGN KEY (StatusId) REFERENCES EncumbranceStatus(Id),
    CONSTRAINT FK_EncumbranceRow_LegalDocument
        FOREIGN KEY (LegalDocumentId) REFERENCES LegalDocument(Id)
);

------------------------------------------------------------
-- 5. DocumentTasks (Subdivision / URW / New Agreements tables)
------------------------------------------------------------

CREATE TABLE DocumentTaskRow (
    Id                        INT IDENTITY(1,1) PRIMARY KEY,
    ProjectId                 INT NOT NULL,
    CategoryId                INT NULL,             -- FK → DocumentCategory (NULL = New Agreements)
    ItemNo                    INT NOT NULL,
    DocDesc                   NVARCHAR(500) NULL,   -- "Document/Desc"
    CopiesDept                NVARCHAR(200) NULL,   -- "copies/dept"
    Signatories               NVARCHAR(500) NULL,
    ConditionOfApproval       NVARCHAR(MAX) NULL,
    CirculationNotes          NVARCHAR(MAX) NULL,
    DocumentStatusId          INT NULL,         -- FK → DocumentTaskStatus
    LegalDocumentTemplateId   INT NULL,         -- FK → LegalDocumentTemplate
    LegalDocumentId           INT NULL,         -- FK → LegalDocument (when signed/registered)
    CONSTRAINT FK_DocumentTaskRow_Project
        FOREIGN KEY (ProjectId) REFERENCES Project(Id)
        ON DELETE CASCADE,
    CONSTRAINT FK_DocumentTaskRow_Category
        FOREIGN KEY (CategoryId) REFERENCES DocumentCategory(Id),
    CONSTRAINT FK_DocumentTaskRow_Status
        FOREIGN KEY (DocumentStatusId) REFERENCES DocumentTaskStatus(Id),
    CONSTRAINT FK_DocumentTaskRow_Template
        FOREIGN KEY (LegalDocumentTemplateId) REFERENCES LegalDocumentTemplate(Id),
    CONSTRAINT FK_DocumentTaskRow_LegalDocument
        FOREIGN KEY (LegalDocumentId) REFERENCES LegalDocument(Id)
);

------------------------------------------------------------
-- 6. Optional: seed some categories & statuses (example only)
------------------------------------------------------------

-- Document categories
INSERT INTO DocumentCategory (Code, Name)
VALUES ('SUBDIVISION', 'Subdivision Plan / Related Docs'),
       ('URW',         'Utility Right of Way'),
       ('NEW_AGREEMENT', 'New Agreements Concurrent with Registration');

-- Document task statuses
INSERT INTO DocumentTaskStatus (Code, Label)
VALUES ('NOT_STARTED',     'Not Started'),  
       ('PREPARED',        'Prepared'),
       ('COMPLETED',       'Completed');

-- Encumbrance actions
INSERT INTO EncumbranceAction (Code, Label)
VALUES ('NO_ACTION_REQUIRED', 'No Action Required'),
       ('CONSENT', 'Consent'),
       ('PARTIAL_DISCHARGE', 'Partial Discharge'),
       ('FULL_DISCHARGE', 'Full Discharge');

-- Encumbrance statuses
INSERT INTO EncumbranceStatus (Code, Label)
VALUES ('NO_ACTION_REQUIRED', 'No Action Required'),
         ('PREPARED', 'Prepared'),
         ('COMPLETE', 'Complete'),
         ('CLIENT_FOR_EXECUTION', 'Client for Execution'),
         ('CITY_FOR_EXECUTION', 'City for Execution'),
         ('THIRD_PARTY_FOR_EXECUTION', 'Third Party for Execution');

-- ALS Surveyors (add mmissing information later )
INSERT INTO SurveyorALS (Name, FtpNumber, City)
VALUES ('Meredith Bryan', '', ''), 
        ('Cathy Wilson', '', ''),
       ('James Durant', '', ''); 
