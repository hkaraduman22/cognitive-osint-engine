unit LoginForm;

interface

uses
  Winapi.Windows,
  Winapi.Messages,
  System.SysUtils,
  System.Variants,
  System.Classes,
  Vcl.Graphics,
  Vcl.Controls,
  Vcl.Forms,
  Vcl.Dialogs,
  Vcl.StdCtrls;

type
  TFrmLogin = class(TForm)
    LblTitle: TLabel;
    LblUsername: TLabel;
    LblPassword: TLabel;
    EdtUsername: TEdit;
    EdtPassword: TEdit;
    BtnLogin: TButton;
    BtnOpenRegister: TButton;
    LblStatus: TLabel;
    procedure BtnLoginClick(Sender: TObject);
    procedure BtnOpenRegisterClick(Sender: TObject);
  private
    procedure SetBusy(const AValue: Boolean);
  public
    { Public declarations }
  end;

var
  FrmLogin: TFrmLogin;

implementation

{$R *.dfm}

uses
  UAuthService,
  UJwtTokenStore,
  RegisterForm,
  MainForm;

procedure TFrmLogin.BtnLoginClick(Sender: TObject);
var
  LAuthService: TAuthService;
  LToken: string;
begin
  SetBusy(True);
  try
    LblStatus.Caption := 'Giris yapiliyor...';
    LAuthService := TAuthService.Create;
    try
      LToken := LAuthService.Login(Trim(EdtUsername.Text), EdtPassword.Text);
      TJwtTokenStore.SetToken(LToken);
    finally
      LAuthService.Free;
    end;

    LblStatus.Caption := 'Giris basarili. JWT kaydedildi.';
    if not Assigned(FrmMain) then
      Application.CreateForm(TFrmMain, FrmMain);

    FrmMain.SetSessionUser(Trim(EdtUsername.Text));
    FrmMain.Show;
    Hide;
  except
    on E: Exception do
      LblStatus.Caption := E.Message;
  end;
  SetBusy(False);
end;

procedure TFrmLogin.BtnOpenRegisterClick(Sender: TObject);
begin
  with TFrmRegister.Create(Self) do
  try
    if ShowModal = mrOk then
      LblStatus.Caption := 'Kayit tamamlandi. Giris aktif.';
  finally
    Free;
  end;
end;

procedure TFrmLogin.SetBusy(const AValue: Boolean);
begin
  BtnLogin.Enabled := not AValue;
  BtnOpenRegister.Enabled := not AValue;
  EdtUsername.Enabled := not AValue;
  EdtPassword.Enabled := not AValue;
end;

end.
